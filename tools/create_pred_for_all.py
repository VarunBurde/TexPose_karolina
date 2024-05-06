import subprocess
import os
import json
import multiprocessing as mp

ycbv_path = "/home/shared_data/datasets/YCBV"
max_instance_inid = "max_instances_inid.json"
codebase_path = "/home/varunburde/Projects/TexPose_karolina"
pred_file = os.path.join(codebase_path, "tools" ,"create_scene_pred_init_calib.py")

max_instance_inid_path = os.path.join(ycbv_path, "ycbv", "train_indi", max_instance_inid)
max_instance_inid = json.load(open(max_instance_inid_path, 'r'))

finished_objects = []
finished_objects_txt = os.path.join( codebase_path, "tools", "finished_objects.txt")



YCB_ID2NAME = {
    1: "002_master_chef_can", 2: "003_cracker_box", 3: "004_sugar_box", 4: "005_tomato_soup_can", 5: "006_mustard_bottle",
    6: "007_tuna_fish_can", 7: "008_pudding_box", 8: "009_gelatin_box", 9: "010_potted_meat_can", 10: "011_banana",
    11: "019_pitcher_base", 12: "021_bleach_cleanser", 13: "024_bowl", 14: "025_mug", 15: "035_power_drill",
    16: "036_wood_block", 17: "037_scissors", 18: "040_large_marker", 19: "051_large_clamp", 20: "052_extra_large_clamp",
    21: "061_foam_brick"
}

nohop_ouput_path = "/home/varunburde/Projects/TexPose_karolina/nohup_output"

def train_object(input_dir, object_id, device):

    #export CUDA_VISIBLE_DEVICES=0
    os.environ["CUDA_VISIBLE_DEVICES"] = str(device)
    print("Training object: ", YCB_ID2NAME[int(object_id)] , " on device: ", device)

    ## compute box
    compute_box_script = os.path.join(codebase_path, "compute_box.py")
    input_string_box = ("--pred_loop=init_calib --save_predbox --generate_pred --target_folder={} --dataset=ycbv "
                        "--root={} --object_id={}").format(input_dir, ycbv_path, object_id)

    # command_box = "nohup python3 {} {} ".format(compute_box_script, input_string_box)
    command_box = "nohup python3 {} {} > {}/{}_{}.out".format(compute_box_script, input_string_box, nohop_ouput_path,
                                                              YCB_ID2NAME[int(object_id)], "box")
    # print(command_box)
    subprocess.call(command_box, shell=True)

    # compute surfline
    compute_surfline_script = os.path.join(codebase_path, "compute_surfelinfo.py")
    input_string_surfline = (("--model=nerf_adapt_st_gan --yaml=nerf_ycbv_adapt_gan --data.pose_source=predicted "
                    "--data.pose_loop=init_calib --gan= --loss_weight.feat= --batch_size=1 --data.root={} "
                    "--data.dataset=ycbv --render.geo_save_dir={} --name={} --data.object={}").
                             format(ycbv_path, input_dir,YCB_ID2NAME[int(object_id)], YCB_ID2NAME[int(object_id)]))
    command_surfline = "nohup python3 {} {} > {}/{}_{}.out".format(compute_surfline_script, input_string_surfline,
                                                                  nohop_ouput_path, YCB_ID2NAME[int(object_id)], "surfline")

    # print(command_surfline)
    subprocess.call(command_surfline, shell=True)

    # # train
    train_script = os.path.join(codebase_path, "train.py")
    input_string_train = ("--model=nerf_adapt_st_gan --yaml=nerf_ycbv_adapt_gan --data.pose_source=predicted "
                         "--data.preload=true --data.scene=scene_all --name={} --data.object={}"
                          .format(YCB_ID2NAME[int(object_id)], YCB_ID2NAME[int(object_id)]))

    command_train = "nohup python3 {} {} > {}/{}_{}.out".format(train_script, input_string_train,
                                                                nohop_ouput_path, YCB_ID2NAME[int(object_id)], "train")
    # print(command_train)
    subprocess.call(command_train, shell=True)

    # generate novel data
    evaluate_script = os.path.join(codebase_path, "evaluate.py")

    input_string_evaluate = (("--model=nerf_adapt_st_gan --yaml=nerf_ycbv_adapt_gan --batch_size=1 --data.preload=false "
                                "--data.object={} --data.scene=scene_all --name={} --resume "
                                "--syn2real --render.save_path=/home/varunburde/Projects/TexPose_karolina/new_render")
                             .format(YCB_ID2NAME[int(object_id)], YCB_ID2NAME[int(object_id)]))

    command_evaluate = "nohup python3 {} {} > {}/{}_{}.out".format(evaluate_script, input_string_evaluate,
                                                                   nohop_ouput_path, YCB_ID2NAME[int(object_id)], "render")

    print(command_evaluate)
    subprocess.call(command_evaluate, shell=True)
    print("\n\n")

    # add object to finished_objects
    with open(finished_objects_txt, 'a') as f:
        f.write(object_id + "\n")


# create pred box
# input_string = "--input_dir {} --object_id {}".format(input_dir, object_id)
# command = "python {} {}".format(pred_file, input_string)
# print(command)
# subprocess.call(command, shell=True)
# finished_objects_list = [1,6,8,11,14,17,19]

available_devices = [2]

if __name__ == '__main__':
    # if finished_objects doesnt exist, create it
    if not os.path.exists(finished_objects_txt):
        with open(finished_objects_txt, 'w') as f:
            f.write("")

    processes = []
    # Only start as many processes as there are devices

    for device in available_devices:
        for instance_id in max_instance_inid.keys():
            object_id = instance_id
            if object_id != str(3):
                continue
            print(object_id)
            image_dataset =  max_instance_inid[instance_id]
            input_dir = os.path.join(ycbv_path,"ycbv", "train_indi", image_dataset)
            print("object_id: ", object_id, " image_dataset: ", image_dataset, input_dir)

            # if int(object_id) in finished_objects_list:
            #     continue

            # if available_devices == []:
            #     for p in processes:
            #         p.join()
            #
            #     print("all devices are busy now")
            #
            #     available_devices = [2, 3, 4]
            #     processes = []

            # device = available_devices.pop(0)
            p = mp.Process(target=train_object, args=(input_dir, object_id, device))
            processes.append(p)
            p.start()

    for p in processes:
        p.join()
