"""Download original, third-party public EPF benchmark CSV to an ignored local directory.

Data are retrieved from the original Zenodo record through the user's own
connection. No redistribution/upload to the HCH repository is performed.
"""
from __future__ import annotations
import argparse
import pathlib
import tempfile
import urllib.request
import sys
import pandas as pd

SOURCE="https://zenodo.org/records/4624805/files/"
NAMES=("DE","PJM","NP","FR","BE")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",choices=NAMES,required=True)
    ap.add_argument("--output-dir",default="data/public")
    ap.add_argument("--dry-run",action="store_true")
    a=ap.parse_args()
    url=SOURCE+a.dataset+".csv"
    dest=pathlib.Path(a.output_dir).resolve()/f"{a.dataset}.csv"
    if a.dry_run:
        print(f"SOURCE={url}\nTARGET={dest}\nLICENSE=review original publisher terms before reuse")
        return
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        print("Already present; refusing overwrite:",dest)
        return
    request=urllib.request.Request(url,headers={"User-Agent":"hch-research-artifact/0.1"})
    with urllib.request.urlopen(request,timeout=60) as response, tempfile.NamedTemporaryFile(
        dir=dest.parent,suffix=".part",delete=False) as tmp:
        tmp_path=pathlib.Path(tmp.name)
        while True:
            chunk=response.read(65536)
            if not chunk:break
            tmp.write(chunk)
    try:
        data=pd.read_csv(tmp_path)
        if len(data)<100 or "Price" not in data.columns:
            raise ValueError("download is not a recognizable EPF benchmark CSV")
        tmp_path.replace(dest)
        print(f"Downloaded {a.dataset}: {len(data)} rows -> {dest}")
        print("This is SOURCE DATA only; no frozen Host predictions/issue-time cache constructed.")
    finally:
        if tmp_path.exists():tmp_path.unlink()

if __name__=="__main__":
    try:main()
    except (ValueError,OSError,urllib.error.URLError) as e:
        print(str(e),file=sys.stderr);raise SystemExit(2) from e
