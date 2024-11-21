from gem5.resources.resource import WorkloadResource, obtain_resource,DiskImageResource
from pathlib import Path

file_path = Path(__file__).resolve().parent

disk_image_base_path = Path(file_path/"../../gem5-resources/src/ubuntu-generic-diskimages")
checkpoint_base_path = Path(file_path/"../workloads/checkpoints/workload-cpts")

def get_arm_npb_workload(rid: int = None, bench: str = None):
    workload = WorkloadResource(
        function = "set_kernel_disk_workload",
        parameters = {
            "kernel" : obtain_resource(resource_id="arm64-linux-kernel-5.15.36"),
            "disk_image" : DiskImageResource(local_path=Path(disk_image_base_path/"arm-disk-image-24-04/arm-nugget-C-8-threads-disk"),root_partition="2"),
            "bootloader" : obtain_resource(resource_id="arm64-bootloader-foundation"),
            "checkpoint" : Path(checkpoint_base_path/f"arm-{bench}-{rid}-cpt")
        }
    )
    return workload
