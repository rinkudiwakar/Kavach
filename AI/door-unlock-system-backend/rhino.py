"""
Rhino utilities for intent recognition from audio.
Handles speech-to-intent processing using Picovoice Rhino.
"""

import os
import logging
from typing import Dict, Optional
import pvrhino
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rhino configuration
RHINO_ACCESS_KEY = os.getenv("RHINO_ACCESS_KEY")
RHINO_CONTEXT_PATH = os.getenv("RHINO_CONTEXT_PATH")


class RhinoUtils:
    """Utility class for intent recognition using Picovoice Rhino."""

    def __init__(
        self,
        access_key: str = RHINO_ACCESS_KEY,
        context_path: str = RHINO_CONTEXT_PATH
    ):
        self.access_key = access_key
        self.context_path = context_path
        self.rhino = None
        self.cleaned_up = False  # Track cleanup status

        try:
            self.rhino = pvrhino.create(
                access_key=access_key,
                context_path=context_path
            )
            logger.info("Rhino engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Rhino: {e}")
            logger.error("Please check your access key and context path")

    def process_audio(self, wav_path: str) -> Dict[str, any]:
        """
        Process WAV audio file and extract intent and slots.
        Args:
            wav_path: Path to WAV audio file (16kHz, mono, 16-bit)
        Returns:
            Dict containing: is_understood, intent, slots, error
        """
        result = {
            'is_understood': False,
            'intent': None,
            'slots': None,
            'error': None
        }

        try:
            if self.rhino is None:
                result['error'] = "Rhino engine not initialized"
                logger.error(result['error'])
                return result

            if not os.path.exists(wav_path):
                result['error'] = f"Audio file not found: {wav_path}"
                logger.error(result['error'])
                return result

            import wave
            import struct

            with wave.open(wav_path, 'rb') as wav_file:
                # Validate format
                if wav_file.getnchannels() != 1:
                    result['error'] = "Audio must be mono"
                    return result
                if wav_file.getframerate() != self.rhino.sample_rate:
                    result['error'] = f"Sample rate must be {self.rhino.sample_rate} Hz"
                    return result
                if wav_file.getsampwidth() != 2:
                    result['error'] = "Audio must be 16-bit"

                num_frames = wav_file.getnframes()
                audio_data = wav_file.readframes(num_frames)
                audio_samples = struct.unpack(f'{num_frames}h', audio_data)

            # Process frames
            frame_length = self.rhino.frame_length
            for i in range(0, len(audio_samples), frame_length):
                frame = audio_samples[i:i + frame_length]
                if len(frame) < frame_length:
                    frame = list(frame) + [0] * (frame_length - len(frame))
                is_finalized = self.rhino.process(frame)
                if is_finalized:
                    inference = self.rhino.get_inference()
                    result['is_understood'] = inference.is_understood
                    if inference.is_understood:
                        result['intent'] = inference.intent
                        result['slots'] = inference.slots
                        logger.info(f"Intent detected: {inference.intent}")
                        logger.info(f"Slots: {inference.slots}")
                    self.rhino.reset()
                    break

            return result

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error processing audio with Rhino: {e}")
            return result

    def get_context_info(self) -> Optional[str]:
        """Return loaded context info"""
        try:
            if self.rhino is None:
                return None
            return self.rhino.context_info
        except Exception as e:
            logger.error(f"Error getting context info: {e}")
            return None

    def cleanup(self):
        """Clean up Rhino resources only once"""
        if not self.cleaned_up and self.rhino is not None:
            try:
                self.rhino.delete()
                self.cleaned_up = True
                logger.info("Rhino engine cleaned up")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")


def process_wav_for_intent(wav_path: str) -> Dict[str, any]:
    """Convenience function to process WAV file and get intent"""
    rhino = RhinoUtils()
    result = rhino.process_audio(wav_path)
    rhino.cleanup()
    return result


# if __name__ == "__main__":
#     logger.info("Testing Rhino utilities...")
#     if RHINO_ACCESS_KEY == "your-picovoice-access-key":
#         logger.warning("Set RHINO_ACCESS_KEY in .env")
#     if RHINO_CONTEXT_PATH == "path/to/context.rhn":
#         logger.warning("Set RHINO_CONTEXT_PATH in .env")

#     try:
#         rhino = RhinoUtils()
#         context_info = rhino.get_context_info()
#         if context_info:
#             logger.info(f"Context info:\n{context_info}")
#         rhino.cleanup()
#     except Exception as e:
#         logger.error(f"Failed to initialize Rhino: {e}")
#     logger.info("Rhino utilities test completed.")