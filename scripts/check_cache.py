"""Validate the schema of a user-supplied, target-free issued-forecast NPZ."""
from __future__ import annotations
import argparse
from hch.data_loader import load_issued_cache

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path",help="Path to an already-authorized forecast-cache NPZ")
    args=ap.parse_args()
    cache=load_issued_cache(args.path)
    print("SCHEMA PASS")
    print("market",cache.market,"frozen_base",cache.base_id)
    print("origins",len(cache.origin_time),"channels",cache.future_state.shape[-1])
    print("roles",{str(role):int((cache.split==role).sum()) for role in sorted(set(cache.split))})
    print("NOTE: upstream issue-time legality and dataset authorization are not certified by this check.")

if __name__=="__main__":
    main()
