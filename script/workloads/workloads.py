from gem5.resources.resource import WorkloadResource, obtain_resource,DiskImageResource
from pathlib import Path

file_path = Path(__file__).resolve().parent

disk_image_base_path = Path(file_path/"../../gem5-resources/src/nugget-disk")
checkpoint_base_path = Path(file_path/"checkpoints")

def get_arm_npb_workload(rid = None, bench = None, thread = 8, size = "C", region_length = 1000_000_000):
    workload = WorkloadResource(
        function = "set_kernel_disk_workload",
        parameters = {
            "kernel" : obtain_resource(resource_id="arm64-linux-kernel-5.15.36"),
            "disk_image" : DiskImageResource(local_path=Path(disk_image_base_path/"arm-disk-image-24-04/arm-nugget-disk"),root_partition="2"),
            "bootloader" : obtain_resource(resource_id="arm64-bootloader-foundation")
        }
    )
    if rid is not None:
        workload.set_parameter("readfile_contents", f"echo 12345 | sudo -S -E LD_LIBRARY_PATH=/home/gem5/nugget-protocol-NPB/common/aarch64-unknown-linux-gnu:LD_LIBRARY_PATH OMP_NUM_THREADS={thread} /home/gem5/nugget-protocol-NPB/{bench.upper()}/{size}/c_m5_fs_measuring/{thread}/{region_length}/{rid}/aarch64/{bench}_aarch64_*.c_m5_fs_measuring;")
    return workload

def get_x86_npb_workload(rid = None, bench = None, thread = 8, size = "C", region_length=1000_000_000):
    workload =  WorkloadResource(
        function = "set_kernel_disk_workload",
        parameters = {
            "kernel_args" : [
                "earlyprintk=ttyS0",
                "console=ttyS0",
                "lpj=7999923",
                "root=/dev/sda2"
            ],
            "kernel" : obtain_resource("x86-linux-kernel-5.4.0-105-generic"),
            "disk_image" : DiskImageResource(local_path=Path(disk_image_base_path/"x86-disk-image-24-04/x86-nugget-disk")),
        }
    )
    if rid is not None:
        workload.set_parameter("readfile_contents", f"echo 12345 | sudo -S -E LD_LIBRARY_PATH=/home/gem5/nugget-protocol-NPB/common/x86_64-unknown-linux-gnu:LD_LIBRARY_PATH OMP_NUM_THREADS={thread} /home/gem5/nugget-protocol-NPB/{bench.upper()}/{size}/c_m5_fs_measuring/{thread}/{region_length}/{rid}/x86_64/{bench}_x86_64_*.c_m5_fs_measuring;")
    return workload
[]