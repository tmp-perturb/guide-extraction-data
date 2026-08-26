#!/usr/bin/env python3
"""Omnibenchmark data-importer module: guide_extraction_data.

This module does NO data processing. Its sole job is to make pre-existing,
externally-hosted input files visible as first-stage outputs of the benchmark
DAG, so downstream stages can consume them via `outputs.id` wiring.

Each declared input is given as a parameter holding an absolute path (or a
comma-separated list of paths). Materialisation:
  - a single path            -> a symlink (no copy; safe for large read-only
                                inputs such as the 10 GB reference matrix);
  - a comma-separated list   -> concatenation into one file (valid for gzip
                                members, e.g. the per-SRR sgRNA FASTQ of a lane).

Omnibenchmark CLI contract:
    --output_dir <dir> --name <node_id>
    --guide_csv <path>            (one path)
    --gex_h5 <path>               (one path)
    --sgRNA_r1 <path[,path...]>   (per-lane FASTQ parts)
    --sgRNA_r2 <path[,path...]>   (per-lane FASTQ parts)
    --reference <path>            (one path; extraction reference matrix, h5ad)

Outputs written into <output_dir> (names match the plan outputs.path with
{dataset} substituted from --name):
    {name}_guide_csv.csv
    {name}_gex.h5
    {name}_sgRNA_r1.fastq.gz
    {name}_sgRNA_r2.fastq.gz
    {name}_reference.h5ad
"""
import argparse
import os
import shutil


def _materialise(paths_csv, out_path):
    parts = [p for p in paths_csv.split(",") if p]
    missing = [p for p in parts if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError("input path(s) not found: " + ", ".join(missing))
    if os.path.lexists(out_path):
        os.remove(out_path)
    if len(parts) == 1:
        # symlink: no duplication of large read-only inputs
        os.symlink(os.path.abspath(parts[0]), out_path)
        print(f"  linked {out_path} -> {parts[0]}", flush=True)
    else:
        with open(out_path, "wb") as out:
            for p in parts:
                with open(p, "rb") as fh:
                    shutil.copyfileobj(fh, out)
        print(f"  concatenated {len(parts)} parts -> {out_path}", flush=True)


def main():
    p = argparse.ArgumentParser(description="Omnibenchmark data importer")
    p.add_argument("--output_dir", required=True)
    p.add_argument("--name", default="dataset")
    p.add_argument("--guide_csv", required=True)
    p.add_argument("--gex_h5", required=True)
    p.add_argument("--sgRNA_r1", required=True)
    p.add_argument("--sgRNA_r2", required=True)
    p.add_argument("--reference", required=True)
    args = p.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    n = args.name
    _materialise(args.guide_csv, os.path.join(args.output_dir, f"{n}_guide_csv.csv"))
    _materialise(args.gex_h5,    os.path.join(args.output_dir, f"{n}_gex.h5"))
    _materialise(args.sgRNA_r1,  os.path.join(args.output_dir, f"{n}_sgRNA_r1.fastq.gz"))
    _materialise(args.sgRNA_r2,  os.path.join(args.output_dir, f"{n}_sgRNA_r2.fastq.gz"))
    _materialise(args.reference, os.path.join(args.output_dir, f"{n}_reference.h5ad"))
    print("guide_extraction_data: staged 5 inputs for", n)


if __name__ == "__main__":
    main()
