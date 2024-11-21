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
parser.add_argument("--checkpoint-output-dir", help="The directory to store the checkpoints", required=True, type=str)
parser.add_argument("--arch", help="The architecture to run the workloads on", required=True, type=str, choices=["riscv", "arm", "x86"])
args = parser.parse_args()

checkpoint_output_dir = Path(args.checkpoint_output_dir)

if args.arch == "arm":
    requires(isa_required=ISA.ARM, coherence_protocol_required=CoherenceProtocol.CHI)
    from script.boards.arm_board import *
    from script.workloads.workloads import get_arm_npb_workload
    checkpoint_output_dir = Path(checkpoint_output_dir/f"arm-bootup-cpt")
    workload = get_arm_npb_workload()
    board = get_KVM_board()
elif args.arch == "x86":
    requires(isa_required=ISA.X86, coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL)
    from script.boards.x86_board import *
    from script.workloads.workloads import get_x86_npb_workload
    checkpoint_output_dir = Path(checkpoint_output_dir/f"x86-bootup-cpt")
    workload = get_x86_npb_workload()
    board = get_KVM_board()

def handle_exit():
    print("kernel exit")
    yield False
    print("init exit")
    m5.checkpoint(checkpoint_output_dir.as_posix())
    yield True

board.set_workload(workload)

simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.EXIT: handle_exit()
})

simulator.run()

print("Simulation finished!")
