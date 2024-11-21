import sys
from pathlib import Path
import argparse

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
file_path = Path(__file__).resolve().parent

from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent

from gem5.utils.requires import requires
from gem5.isas import ISA
from gem5.coherence_protocol import CoherenceProtocol

import m5

parser = argparse.ArgumentParser(description="Take checkpoints after booting the system")
parser.add_argument("--rid", help="The resource id of the workload", required=True, type=int)
parser.add_argument("--checkpoint-output-dir", help="The directory to store the checkpoints", required=True, type=str)
parser.add_argument("--arch", help="The architecture to run the workloads on", required=True, type=str, choices=["riscv", "arm", "x86"])
parser.add_argument("--bootup-cpt", help="Whether to get the bootup checkpoint", type=str)
parser.add_argument("--bench", help="The benchmark to run", type=str)
parser.add_argument("--thread-size", help="The number of threads to run the workloads with", required=False, type=int, default=8)
parser.add_argument("--region-length", help="The region length of the workloads", required=False, type=int, default=1000_000_000)
parser.add_argument("--class-size", help="The size of the workloads", required=False, type=str, default="C")
args = parser.parse_args()

rid = args.rid
bench = args.bench
bootup_cpt = Path(args.bootup_cpt)

thread_size = args.thread_size
region_length = args.region_length
class_size = args.class_size

checkpoint_output_dir = Path(args.checkpoint_output_dir)

if args.arch == "arm":
    requires(isa_required=ISA.ARM, coherence_protocol_required=CoherenceProtocol.CHI)
    from script.boards.arm_board import *
    from script.workloads.workloads import get_arm_npb_workload
    checkpoint_output_dir = Path(checkpoint_output_dir/f"arm-{bench}-{rid}-cpt")
    workload = get_arm_npb_workload(rid, bench, thread=thread_size, size=class_size, region_length=region_length)
    workload.set_parameter("checkpoint", bootup_cpt)
    board = get_KVM_board()
elif args.arch == "x86":
    requires(isa_required=ISA.X86, coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL)
    from script.boards.x86_board import *
    from script.workloads.workloads import get_x86_npb_workload
    checkpoint_output_dir = Path(checkpoint_output_dir/f"x86-{bench}-{rid}-cpt")
    workload = get_x86_npb_workload(rid, bench, thread=thread_size, size=class_size, region_length=region_length)
    workload.set_parameter("checkpoint", bootup_cpt)
    board = get_KVM_board()

def ignore_all_exit():
    while True:
        yield False

def handel_workbegin(cpt_output_dir):
    print("Encounter workbegin event, take a checkpoint.")
    print(f"Current tick: {m5.curTick()}")
    m5.checkpoint(cpt_output_dir)
    yield True

board.set_workload(workload)

simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.WORKBEGIN: handel_workbegin(checkpoint_output_dir.as_posix()),
        ExitEvent.EXIT: ignore_all_exit()
})

simulator.run()

print("Simulation finished!")
