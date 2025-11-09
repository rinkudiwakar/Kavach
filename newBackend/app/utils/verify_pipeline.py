



# verify_voice.py
from __future__ import annotations
import io
import json
import os
import tempfile
import wave
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional

import numpy as np
from pydub import AudioSegment
import webrtcvad
from vosk import Model, KaldiRecognizer
from resemblyzer import VoiceEncoder, preprocess_wav
from pymongo import MongoClient
from dotenv import load_dotenv

# -----------------------
# Defaults (override via env/args)
# -----------------------
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_MIN_KWS_CONF = 0.70
DEFAULT_SPK_THRESHOLD = 0.65
DEFAULT_VAD_FRAME_MS = 30
DEFAULT_VAD_AGGR = 2
DEFAULT_MIN_VOICE_SECS = 1.2

# Keep a cached Vosk model (avoid reload on each call)
_VOSK_MODEL: Optional[Model] = None

# -----------------------
# Mongo / config helpers
# -----------------------
def _get_mongo() -> tuple[MongoClient, str, str]:
    load_dotenv()
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB", "voice_door_unlock")
    coll_name = os.getenv("MONGODB_FAMILY_COLL", "family_admin")
    return MongoClient(uri), db_name, coll_name

def _fetch_single_family_members() -> List[dict]:
    """
    Returns members[] from the single family_admin document.
    Assumes exactly one family exists in the collection.
    """
    client, db_name, coll_name = _get_mongo()
    coll = client[db_name][coll_name]
    doc = coll.find_one({}, {"members": 1})
    if not doc or "members" not in doc:
        raise ValueError("No family document found or it has no members")
    return doc["members"]

# -----------------------
# Audio helpers
# -----------------------
# def _to_wav16k_mono_temp(audio: Union[str, Path, bytes]) -> Path
    """
    Accepts a file path or bytes. Returns a temp 16kHz mono 16-bit WAV Path.
    """
    if isinstance(audio, (str, Path)):
        seg = AudioSegment.from_file(audio)
    elif isinstance(audio, (bytes, bytearray)):
        seg = AudioSegment.from_file(io.BytesIO(audio))
    else:
        raise TypeError("audio must be a path or bytes")

    seg = seg.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    out = Path(tmp)
    seg.export(out, format="wav")
    return out
def _to_wav16k_mono_temp(audio: Union[str, Path, bytes]) -> Path:
    """
    Convert input to mono 16kHz 16-bit WAV in a temp file.
    - WAV inputs handled without ffmpeg (no pydub needed)
    - Non-WAV fall back to pydub (requires ffmpeg)
    """
    def _write_wav(path: Path, data: bytes, sr: int):
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(data)

    # Load bytes
    if isinstance(audio, (str, Path)):
        with open(audio, "rb") as f:
            raw = f.read()
        ext = str(audio).lower().rsplit(".", 1)[-1] if "." in str(audio) else ""
    elif isinstance(audio, (bytes, bytearray)):
        raw = bytes(audio)
        ext = ""  # unknown
    else:
        raise TypeError("audio must be a path or bytes")

    # If WAV header, do pure-python convert (no ffmpeg)
    if raw[:4] == b"RIFF" and raw[8:12] == b"WAVE" or ext == "wav":
        import audioop
        with wave.open(io.BytesIO(raw), "rb") as wf:
            nch = wf.getnchannels()
            sw  = wf.getsampwidth()
            sr  = wf.getframerate()
            frames = wf.readframes(wf.getnframes())

        # Ensure 16-bit PCM
        if sw != 2:
            frames = audioop.lin2lin(frames, sw, 2)

        # To mono (take first channel)
        if nch > 1:
            frames = audioop.tomono(frames, 2, 1.0, 0.0)

        # Resample to 16k if needed
        if sr != 16000:
            frames, _ = audioop.ratecv(frames, 2, 1, sr, 16000, None)
            sr = 16000

        fd, tmp = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        out = Path(tmp)
        _write_wav(out, frames, sr)
        return out

    # Fallback for MP3/M4A/etc. -> requires ffmpeg
    from pydub import AudioSegment
    seg = AudioSegment.from_file(io.BytesIO(raw))
    seg = seg.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    out = Path(tmp)
    seg.export(out, format="wav")
    return out

def _wav_to_float32(wav16_path: Path, sample_rate: int) -> np.ndarray:
    with wave.open(str(wav16_path), "rb") as wf:
        assert wf.getframerate() == sample_rate and wf.getnchannels() == 1
        raw = wf.readframes(wf.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

def _vad_filter(
    wave_f32: np.ndarray,
    sr: int,
    frame_ms: int,
    aggressiveness: int
) -> np.ndarray:
    """
    WebRTC VAD voiced-only extraction. Returns float32 waveform.
    """
    vad = webrtcvad.Vad(aggressiveness)
    frame_len = int(sr * frame_ms / 1000)  # samples/frame
    pcm16 = np.clip(wave_f32 * 32768.0, -32768, 32767).astype(np.int16).tobytes()

    voiced_chunks: List[np.ndarray] = []
    frame_bytes = frame_len * 2
    for i in range(0, len(pcm16), frame_bytes):
        chunk = pcm16[i:i + frame_bytes]
        if len(chunk) < frame_bytes:
            break
        if vad.is_speech(chunk, sr):
            arr = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
            voiced_chunks.append(arr)

    if not voiced_chunks:
        return np.array([], dtype=np.float32)
    return np.concatenate(voiced_chunks)

# -----------------------
# Vosk (keyword spotting)
# -----------------------
def _load_vosk_model(model_path: Union[str, Path]) -> Model:
    global _VOSK_MODEL
    if _VOSK_MODEL is None:
        mp = Path(model_path)
        if not mp.exists():
            raise FileNotFoundError(f"Vosk model not found: {mp}")
        _VOSK_MODEL = Model(str(mp))
    return _VOSK_MODEL

def _vosk_keyword_check(
    wav16_path: Path,
    keywords: List[str],
    min_conf: float,
    sample_rate: int
) -> Tuple[bool, List[dict]]:
    kws_set = {k.lower() for k in keywords if k}
    rec = KaldiRecognizer(_VOSK_MODEL, sample_rate, json.dumps(sorted(list(kws_set)) + ["[unk]"]))
    rec.SetWords(True)

    hits: List[dict] = []
    with wave.open(str(wav16_path), "rb") as wf:
        while True:
            data = wf.readframes(8000)
            if not data:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                for w in result.get("result", []):
                    token = (w.get("word") or "").lower()
                    conf = float(w.get("conf", 0.0))
                    if token in kws_set and conf >= min_conf:
                        hits.append({
                            "keyword": token,
                            "conf": conf,
                            "start_s": float(w.get("start", 0.0)),
                            "end_s": float(w.get("end", 0.0)),
                        })
    final = json.loads(rec.FinalResult())
    for w in final.get("result", []):
        token = (w.get("word") or "").lower()
        conf = float(w.get("conf", 0.0))
        if token in kws_set and conf >= min_conf:
            hits.append({
                "keyword": token,
                "conf": conf,
                "start_s": float(w.get("start", 0.0)),
                "end_s": float(w.get("end", 0.0)),
            })
    return (len(hits) > 0), hits

# -----------------------
# Speaker verification
# -----------------------
def _embed_wave(wave_f32: np.ndarray, sample_rate: int) -> np.ndarray:
    enc = VoiceEncoder()
    wav_proc = preprocess_wav(wave_f32, source_sr=sample_rate)
    return enc.embed_utterance(wav_proc)

def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

# -----------------------
# Public API
# -----------------------
def verify_voice(
    audio: Union[str, Path, bytes],
    *,
    vosk_model_path: Union[str, Path],
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    min_kws_conf: float = DEFAULT_MIN_KWS_CONF,
    speaker_threshold: float = DEFAULT_SPK_THRESHOLD,
    vad_frame_ms: int = DEFAULT_VAD_FRAME_MS,
    vad_aggressiveness: int = DEFAULT_VAD_AGGR,
    min_voice_secs: float = DEFAULT_MIN_VOICE_SECS,
) -> dict:
    """
    Verification using a SINGLE audio and your one-family schema:
      1) Pull the only family's members (keyword + single 256-D embedding)
      2) Vosk keyword check against union of members' keywords
      3) If keyword found, enforce per-member keyword and score speaker
    Returns a dict:
    {
      "keyword_present": bool,
      "keyword_hits": [ {keyword, conf, start_s, end_s}, ... ],
      "best_match": {"member_id": str|None, "name": str|None, "similarity": float},
      "per_member_scores": {member_id: score, ...},
      "decision": "accepted"|"rejected",
      "config": {...}
    }
    """
    # Load members from the single family doc
    members = _fetch_single_family_members()

    # Build keyword set and embedding map
    keywords: List[str] = []
    member_refs: Dict[str, dict] = {}  # member_id -> {name, keyword, emb(np)}
    for m in members:
        kw = (m.get("keyword") or "").strip().lower()
        if kw:
            keywords.append(kw)
        emb_list = m.get("embedding")
        if isinstance(emb_list, list) and len(emb_list) >= 128:
            ref = np.asarray(emb_list, dtype=np.float32)
            member_refs[m["member_id"]] = {
                "name": m.get("name", ""),
                "keyword": kw,
                "emb": ref
            }

    if not member_refs:
        return {
            "error": "No valid member embeddings found",
            "decision": "rejected"
        }
    if not keywords:
        return {
            "error": "No member keywords configured",
            "decision": "rejected"
        }

    # Prepare model & audio
    _load_vosk_model(vosk_model_path)
    wav16 = _to_wav16k_mono_temp(audio)

    try:
        # 1) Keyword spotting
        keyword_present, hits = _vosk_keyword_check(wav16, keywords, min_kws_conf, sample_rate)

        # 2) Speaker verify (only if KWS passed)
        best_member_id, best_name, best_score = None, None, 0.0
        per_member_scores: Dict[str, float] = {}
        decision = "rejected"

        if keyword_present:
            # choose the spoken keyword (highest conf)
            spoken_kw = max(hits, key=lambda h: h["conf"])["keyword"] if hits else None

            x = _wav_to_float32(wav16, sample_rate)
            voiced = _vad_filter(x, sample_rate, vad_frame_ms, vad_aggressiveness)

            if spoken_kw and voiced.size >= int(min_voice_secs * sample_rate):
                probe = _embed_wave(voiced, sample_rate)

                # score only members whose keyword matches the spoken keyword
                for member_id, info in member_refs.items():
                    if info["keyword"] != spoken_kw:
                        continue
                    score = _cosine_sim(probe, info["emb"])
                    per_member_scores[member_id] = round(float(score), 4)
                    if score > best_score:
                        best_score = float(score)
                        best_member_id = member_id
                        best_name = info["name"]

                if best_member_id and best_score >= speaker_threshold:
                    decision = "accepted"

        return {
            "keyword_present": bool(keyword_present),
            "keyword_hits": hits,
            "best_match": {
                "member_id": best_member_id,
                "name": best_name,
                "similarity": round(float(best_score), 4)
            },
            "per_member_scores": per_member_scores,  # only for matching keyword
            "decision": decision,
            "config": {
                "speaker_threshold": float(speaker_threshold),
                "min_kws_conf": float(min_kws_conf),
                "vad": {
                    "frame_ms": int(vad_frame_ms),
                    "aggressiveness": int(vad_aggressiveness),
                    "min_voice_secs": float(min_voice_secs)
                },
                "enforce_keyword_per_member": True
            }
        }
    finally:
        try:
            wav16.unlink(missing_ok=True)
        except Exception:
            pass


# -----------------------
# Quick manual test
# -----------------------
if __name__ == "__main__":
    # Example usage:
    RES = verify_voice(
        audio="user_clip.mp3",  # <- change to your test file
        vosk_model_path=os.getenv("VOSK_MODEL_PATH", r"C:\models\vosk-model-small-en-us-0.15"),
        speaker_threshold=0.65,
        min_kws_conf=0.70,
    )
    print(json.dumps(RES, indent=2))

