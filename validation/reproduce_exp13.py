"""Isolated EXP-13 local HTTP/SQLite integration reproduction.

Usage: python -m validation.reproduce_exp13 --output-dir /tmp/adora-exp13-new
Copies original source scripts into a fresh output tree and executes them there.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/EXP-13"
ORIGINAL = (SOURCE / "results").resolve()

def reproduce(output_dir):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory already exists")
    if dest == ORIGINAL or ORIGINAL in dest.parents or dest in ORIGINAL.parents:
        raise ValueError("Output directory must be separate from original results")
    dest.mkdir(parents=True)
    work = dest / "experiment"
    work.mkdir()
    source_hashes = {}
    for name in ("run_integration.py", "server.py"):
        source = SOURCE / name
        source_hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
        shutil.copyfile(source, work / name)
    execution = subprocess.run(
        [sys.executable, "run_integration.py"],
        cwd=work, capture_output=True, text=True, timeout=120,
    )
    published = json.loads((ORIGINAL / "summary.json").read_text(encoding="utf-8"))
    fresh_file = work / "results/summary.json"
    fresh = json.loads(fresh_file.read_text(encoding="utf-8")) if fresh_file.exists() else None
    manifest = {
        "classification": "NEW_LOCAL_EXP13_REPRODUCTION",
        "source_hashes": source_hashes,
        "original_summary_sha256": hashlib.sha256((ORIGINAL / "summary.json").read_bytes()).hexdigest(),
        "original_requests_sha256": hashlib.sha256((ORIGINAL / "http_requests.csv").read_bytes()).hexdigest(),
        "returncode": execution.returncode,
        "fresh_summary": fresh,
        "published_summary": published,
        "matches_published": fresh == published if fresh is not None else False,
        "execution_environment": "localhost HTTP receiver, SQLite temporary database",
    }
    (dest / "stdout.txt").write_text(execution.stdout, encoding="utf-8")
    (dest / "stderr.txt").write_text(execution.stderr, encoding="utf-8")
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if execution.returncode:
        raise RuntimeError("EXP-13 local reproduction failed; see isolated stderr.txt")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    print(json.dumps(reproduce(parser.parse_args().output_dir), indent=2))
