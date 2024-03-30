import os
import subprocess
import numpy as np

def run_cmd(cmd: str):
    """Run a command in the terminal."""
    print("cmd:", cmd)
    print("output:")
    subprocess.Popen(cmd, shell=True).wait()

dataset_path = "/mnt/proj3/open-29-7/varun_ws/datasets/YCB-V/ycbv/test"
object_id = np.arange(1, 22)

for dir in os.listdir(dataset_path):
    scene_id = dir
    scene_dir = os.path.join(dataset_path, scene_id)
    for object in object_id:
        print("Processing scene: ", scene_dir, "Object: ", object)
        flags = (" --pred_loop init_calib --generate_pred --save_predbox --dataset=ycbv "
                 "--root=/mnt/proj3/open-29-7/varun_ws/datasets/YCB-V/")
        command = ("python3 compute_box.py --target_folder=" + scene_dir + " --object_id="
                   + str(object) + flags)
        run_cmd(command)
