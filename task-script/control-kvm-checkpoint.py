import subprocess
from multiprocessing import Pool
from pathlib import Path
import argparse
import json

parser = argparse.ArgumentParser(description="Take checkpoints at nugget marker for NPB workloads")
parser.add_argument("--gem5-binary", help="The path to the gem5 binary", required=True, type=str)
parser.add_argument("--arch", help="The architecture to run the workloads on", required=True, type=str)
parser.add_argument("--m5out-dir", help="The directory to store the m5outs", required=True, type=str)
parser.add_argument("--checkpoint-dir", help="The directory to store the checkpoints", required=True, type=str)
parser.add_argument("--nugget-info-json", help="The json file that contains the nugget marker information", required=True, type=str)
parser.add_argument("--benchmarks", nargs="+", type=str, default=["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"])
parser.add_argument("--thread-size", help="The number of threads to run the workloads with", required=False, type=int, default=8)
parser.add_argument("--region-length", help="The region length of the workloads", required=False, type=int, default=1000_000_000)
parser.add_argument("--class-size", help="The size of the workloads", required=False, type=str, default="C")
args = parser.parse_args()

gem5_binary = Path(args.gem5_binary)
arch = args.arch
m5out_dir = Path(args.m5out_dir)
checkpoint_dir = Path(args.checkpoint_dir)
nugget_info_json = args.nugget_info_json
benchmarks = args.benchmarks

thread_size = args.thread_size
region_length = args.region_length
class_size = args.class_size

default_cmd = ["cset", "proc", "-s", "measurement", "-e", "--"]

workdir = Path().cwd()
run_file = Path(workdir/f"script/pre-experiment/take-workload-checkpoints.py")

m5out_dir.mkdir(parents=True, exist_ok=True)
checkpoint_dir.mkdir(parents=True, exist_ok=True)

with open(nugget_info_json, "r") as f:
    nugget_info = json.load(f)

def run(this):
    command = default_cmd + this
    print(command)
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Failed to run {command}")
    else:
        print(f"Success to run {command}")
    return result


for bench in benchmarks:
    rep_rids = nugget_info[bench]
    for rid in rep_rids:
        if Path(checkpoint_dir/f"{arch}-{bench}-{rid}-cpt").exists():
            print(f"Checkpoint for {arch}-{bench}-{rid} already exists")
            continue
        run_output = Path(m5out_dir/f"{arch}-{bench}-{rid}-nugget-cpt-m5out")
        cmd = [gem5_binary, "--outdir", run_output, "--bench", bench, "--rid", rid]
        run(cmd)
