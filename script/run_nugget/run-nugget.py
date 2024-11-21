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

parser = argparse.ArgumentParser(description="Run the nugget with detailed board")
parser.add_argument("--rid", help="The resource id of the workload", required=True, type=int)
parser.add_argument("--bench", help="The benchmark to run", type=str)
args = parser.parse_args()

requires(isa_required=ISA.ARM, coherence_protocol_required=CoherenceProtocol.CHI)

rid = int(args.rid)
bench = args.bench

# workload
from gem5.resources.resource import WorkloadResource, obtain_resource,DiskImageResource

disk_image_path = Path(file_path/"../../gem5-resources/src/ubuntu-generic-diskimages/arm-disk-image-24-04/arm-nugget-C-8-threads-disk")
checkpoint_base_path = Path(file_path/"../workloads/checkpoints/workload-cpts")

from script.boards.arm_board import *
workload = WorkloadResource(
    function = "set_kernel_disk_workload",
    parameters = {
        "kernel" : obtain_resource(resource_id="arm64-linux-kernel-5.15.36"),
        "disk_image" : DiskImageResource(local_path=disk_image_path,root_partition="2"),
        "bootloader" : obtain_resource(resource_id="arm64-bootloader-foundation"),
        "checkpoint" : Path(checkpoint_base_path/f"arm-{bench}-{rid}-cpt")
    }
)

board = get_detailed_board()

def handle_workbegin():
    print("Encounter workbegin event, dump and reset the stats.")
    m5.stats.dump()
    m5.stats.reset()
    yield False

def handel_workend():
    print("Encounter workend event, dump the stats.")
    m5.stats.dump()
    yield True

board.set_workload(workload)

simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.WORKEND:handel_workend(),
        ExitEvent.WORKBEGIN: handle_workbegin()
})

simulator.run()

print("Simulation finished!")
