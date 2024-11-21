import subprocess
from multiprocessing import Pool
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description="Take checkpoints at nugget marker for NPB workloads")
parser.add_argument("--gem5-binary", help="The path to the gem5 binary", required=True, type=str)
parser.add_argument("--arch", help="The architecture to run the workloads on", required=True, type=str)
parser.add_argument("--m5out-dir", help="The directory to store the m5outs", required=True, type=str)
parser.add_argument("--checkpoint-dir", help="The directory to store the checkpoints", required=True, type=str)
args = parser.parse_args()

gem5_binary = Path(args.gem5_binary)
arch = args.arch
m5out_dir = Path(args.m5out_dir)
checkpoint_dir = Path(args.checkpoint_dir)

default_cmd = ["cset", "proc", "-s", "measurement", "-e", "--"]

workdir = Path().cwd()

m5out_dir.mkdir(parents=True, exist_ok=True)
checkpoint_dir.mkdir(parents=True, exist_ok=True)

def run(this):
    command = default_cmd + this
    print(command)
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Failed to run {command}")
    else:
        print(f"Success to run {command}")
    return result

run_file = Path(workdir/f"script/pre-experiment/take-bootup-checkpoints.py")
command = [gem5_binary.as_posix(), "-re", "--outdir", 
           Path(m5out_dir/f"{arch}-after-boot-cpt-m5out").as_posix(), 
           run_file.as_posix(),
           "--checkpoint-output-dir", checkpoint_dir.as_posix(), 
           "--arch", arch]
run(command)

print("All Done!")
