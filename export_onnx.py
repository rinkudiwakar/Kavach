# inspect_and_try_export.py
import torch
import traceback
from resemblyzer import VoiceEncoder
import sys
import os

torch.set_num_threads(1)

OUT_DIR = "onnx_exports"
os.makedirs(OUT_DIR, exist_ok=True)

def write_module_tree(enc, out_file="module_tree.txt"):
    with open(out_file, "w", encoding="utf-8") as f:
        for name, mod in enc.named_modules():
            f.write(f"{name!r:40} : {type(mod)}\n")
    print(f"Wrote module tree to {out_file}")

def find_candidate_modules(enc):
    # candidates: named_modules that have at least 1 parameter and aren't the top-level empty name
    candidates = []
    for name, mod in enc.named_modules():
        # skip the top-level wrapper (name == "")
        if name == "":
            continue
        params = sum(p.numel() for p in mod.parameters() if p is not None)
        if params > 0:
            candidates.append((name, mod, params))
    # sort by number params descending (largest modules first)
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates

def try_export(module, example_input, out_path):
    # simple ONNX export attempt
    module.eval()
    module.cpu()
    with torch.no_grad():
        try:
            torch._dynamo.disable()
        except Exception:
            pass
        try:
            print(f"Trying ONNX export: {out_path}  (input shape {tuple(example_input.shape)})")
            torch.onnx.export(
                module,
                example_input,
                out_path,
                opset_version=11,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes=None,
                verbose=False,
                keep_initializers_as_inputs=False,
            )
            print("  -> ONNX export SUCCEEDED:", out_path)
            return True, None
        except Exception as e:
            tb = traceback.format_exc()
            print("  -> ONNX export FAILED:", e)
            return False, tb

def try_torchscript(module, example_input, out_path):
    try:
        module.eval()
        module.cpu()
        print("Trying TorchScript trace ->", out_path)
        ts = torch.jit.trace(module, example_input, strict=False)
        ts.save(out_path)
        print("  -> TorchScript saved:", out_path)
        return True, None
    except Exception as e:
        tb = traceback.format_exc()
        print("  -> TorchScript trace FAILED:", e)
        return False, tb

def main():
    print("Loading VoiceEncoder...")
    enc = VoiceEncoder()
    print("Loaded VoiceEncoder")

    # Write full module tree
    write_module_tree(enc, out_file=os.path.join(OUT_DIR, "module_tree.txt"))

    # Find candidates
    candidates = find_candidate_modules(enc)
    print(f"Found {len(candidates)} candidate submodules with parameters (top ones listed):")
    for i,(name,mod,params) in enumerate(candidates[:20], start=1):
        print(f"{i:02d}. {name!r:40} params={params} type={type(mod)}")

    # If no candidates found, also list named_children (some libs use named_children)
    if not candidates:
        print("No parameterized submodules found. Listing named_children instead:")
        for name, mod in enc.named_children():
            print(name, type(mod))

    # Example inputs to try
    x_mel = torch.randn(1, 1, 80, 250, dtype=torch.float32)
    x_wave = torch.randn(1, 32000, dtype=torch.float32)

    # Try export/tracing for the top N candidates
    TOP_N = 6
    tried = 0
    report = []
    for name, mod, params in candidates[:TOP_N]:
        safe_name = name.replace(".", "_").replace("/", "_")
        onnx_path_mel = os.path.join(OUT_DIR, f"{safe_name}_mel.onnx")
        onnx_path_wave = os.path.join(OUT_DIR, f"{safe_name}_wave.onnx")
        ts_path = os.path.join(OUT_DIR, f"{safe_name}_traced.pt")

        print("\n---")
        print("Candidate:", name, "params:", params, "type:", type(mod))

        ok, tb = try_export(mod, x_mel, onnx_path_mel)
        if ok:
            report.append((name, "onnx", onnx_path_mel))
            continue
        else:
            # try wave shape
            ok2, tb2 = try_export(mod, x_wave, onnx_path_wave)
            if ok2:
                report.append((name, "onnx", onnx_path_wave))
                continue

        # ONNX failed; try TorchScript trace (on mel shape, then wave)
        ok3, tb3 = try_torchscript(mod, x_mel, ts_path)
        if ok3:
            report.append((name, "torchscript", ts_path))
            continue
        ok4, tb4 = try_torchscript(mod, x_wave, ts_path)
        if ok4:
            report.append((name, "torchscript", ts_path))
            continue

        # record failures
        report.append((name, "failed", {"onnx_mel_tb": tb, "onnx_wave_tb": tb2 if 'tb2' in locals() else None,
                                        "ts_mel_tb": tb3 if 'tb3' in locals() else None,
                                        "ts_wave_tb": tb4 if 'tb4' in locals() else None}))
        tried += 1

    # Summary
    summary_path = os.path.join(OUT_DIR, "summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        for item in report:
            f.write(str(item) + "\n\n")
    print("\nAll done. Summary written to", summary_path)
    print("Also: module tree at", os.path.join(OUT_DIR, "module_tree.txt"))
    print("Check the ONNX / TorchScript artifacts (if any) in", OUT_DIR)
    print("If all candidates failed, paste the top portion of", os.path.join(OUT_DIR, "module_tree.txt"), "here and I'll craft a custom wrapper.")

if __name__ == "__main__":
    main()
