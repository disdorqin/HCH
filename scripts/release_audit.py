"""Prevent accidental publication of private artifacts and false-ready code claims."""
from __future__ import annotations
import pathlib,re,sys
root=pathlib.Path(__file__).resolve().parents[1]
forbidden_suffix={".xlsx",".xls",".parquet",".npz",".npy",".pt",".pth",".ckpt",".pkl",".pickle",".db",".sqlite",".zip",".rar",".7z",".pem",".key"}
ignored={".git","__pycache__",".pytest_cache",".venv","build","dist"}
violations=[]
for p in root.rglob("*"):
    if not p.is_file() or any(a in ignored for a in p.relative_to(root).parts):continue
    rel=p.relative_to(root)
    if p.suffix.lower() in forbidden_suffix:violations.append(f"FORBIDDEN_FILE: {rel}")
    if p.stat().st_size>1_500_000:violations.append(f"OVERSIZE_FILE: {rel}")
    if p.suffix.lower() in {".py",".toml",".md",".txt",".yaml",".yml"}:
        s=p.read_text(encoding="utf-8",errors="replace")
        if re.search(r"(?im)^\s*(?:api_key|secret_key|password|access_token)\s*[:=]\s*['\"][^'\"]+['\"]",s):
            violations.append(f"POSSIBLE_SECRET: {rel}")
        if ("-----BEGIN"+" PRIVATE KEY-----") in s:violations.append(f"PRIVATE_KEY: {rel}")
print("Scanned:",root)
print("Found issues:",len(violations))
for v in violations:print(v)
print("RELEASE GATE:", "NOT READY: incomplete reproduction artifacts" if not violations else "BLOCKED")
sys.exit(1 if violations else 0)
