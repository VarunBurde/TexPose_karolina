import os
import json

ycbv_real_path = "/home/shared_data/datasets/YCBV/ycbv/train_indi"
max_instances_json = os.path.join(ycbv_real_path, "max_instances_inid.json")
max_instances = json.load(open(max_instances_json))

scene_pred_init_calib = {}
scene_pred_info = {}
splits = {}

for object_id in max_instances:
    splits[object_id] = {}


for object_id in max_instances:
    dataset_id = max_instances[object_id]
    dataset_path = os.path.join(ycbv_real_path, dataset_id)
    scene_gt_json = os.path.join(dataset_path, "scene_gt.json")
    scene_gt = json.load(open(scene_gt_json))
    scene_gt_info_json = os.path.join(dataset_path, "scene_gt_info.json")
    scene_gt_info = json.load(open(scene_gt_info_json))

    scene_pred_init_calib[dataset_id] = {}
    scene_pred_info[dataset_id] = {}
    splits[object_id][dataset_id] = []

    for img_id in scene_gt:
        for object in range(len(scene_gt[img_id])):
            if str(scene_gt[img_id][object]["obj_id"]) == str(object_id):
                scene_pred_init_calib[dataset_id][img_id] = [scene_gt[img_id][object]]
                scene_pred_info[dataset_id][img_id] = [scene_gt_info[img_id][object]]
                splits[object_id][dataset_id].append(img_id)


# save the splits
splits_json = os.path.join(ycbv_real_path, "splits.json")
with open(splits_json, 'w') as file:
    json.dump(splits, file, indent=2)

splits = os.path.join(ycbv_real_path, "splits.json")
splits = json.load(open(splits))


YCB_data = {
    1: "002_master_chef_can", 2: "003_cracker_box", 3: "004_sugar_box", 4: "005_tomato_soup_can", 5: "006_mustard_bottle",
    6: "007_tuna_fish_can", 7: "008_pudding_box", 8: "009_gelatin_box", 9: "010_potted_meat_can", 10: "011_banana",
    11: "019_pitcher_base", 12: "021_bleach_cleanser", 13: "024_bowl", 14: "025_mug", 15: "035_power_drill",
    16: "036_wood_block", 17: "037_scissors", 18: "040_large_marker", 19: "051_large_clamp", 20: "052_extra_large_clamp",
    21: "061_foam_brick"
}

split_location = "/home/varunburde/Projects/TexPose_karolina/splits/ycbv"
split_list = {}


# create the splits
for object_id in splits:
    object_name = YCB_data[int(object_id)]
    os.makedirs(os.path.join(split_location, object_name, "scene_all"), exist_ok=True)
    split_file_train = os.path.join(split_location, object_name, "scene_all", "train.txt")

    # if split file exists delete it
    if os.path.exists(split_file_train):
        os.remove(split_file_train)

    # create empty split file
    open(split_file_train, 'a').close()

    for dataset_id in splits[object_id]:
        dataset_location = os.path.join(ycbv_real_path, dataset_id)
        split_list[object_name] = []

        for img_id in splits[object_id][dataset_id]:
            string_to_write = object_name + " " + dataset_location + " " + img_id
            split_list[object_name].append(string_to_write)
            with open(split_file_train, 'a') as file:
                file.write(string_to_write + "\n")
        file.close()

for object_id in splits:
    object_name = YCB_data[int(object_id)]
    split_file_test = os.path.join(split_location, object_name, "scene_all", "test.txt")
    split_file_eval = os.path.join(split_location, object_name, "scene_all", "val.txt")

    split_object_list = split_list[object_name]
    split_object_list_len = len(split_object_list)

    # use random list to create the split
    split_object_list_test = split_object_list[:int(split_object_list_len/9)]
    split_object_list_eval = split_object_list[int(split_object_list_len/9):]

    # if split file exists delete it
    if os.path.exists(split_file_test):
        os.remove(split_file_test)
    if os.path.exists(split_file_eval):
        os.remove(split_file_eval)

    # create empty split file
    open(split_file_test, 'a').close()
    open(split_file_eval, 'a').close()

    # use random list to create the split
    for string_to_write in split_object_list_test:
        with open(split_file_test, 'a') as file:
            file.write(string_to_write + "\n")
    file.close()


    for string_to_write in split_object_list_eval:
        with open(split_file_eval, 'a') as file:
            file.write(string_to_write + "\n")
    file.close()





