import os
import pymeshlab


def convert_ply_to_texture(input_ply_file,  output_ply_file):
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(input_ply_file)
    ms.compute_texcoord_transfer_vertex_to_wedge()
    ms.transfer_texture_to_color_per_vertex()
    ms.save_current_mesh(output_ply_file)


if __name__ == '__main__':
    ycbv_model_path = "/home/shared_data/datasets/YCBV/ycbv/models"
    ycbv_model_output_path = "/home/shared_data/datasets/YCBV/ycbv/models_texpose"

    os.makedirs(ycbv_model_output_path, exist_ok=True)

    for model in os.listdir(ycbv_model_path):
        if model.endswith(".ply"):
            input_ply_file = os.path.join(ycbv_model_path, model)
            output_ply_file = os.path.join(ycbv_model_output_path, model)
            convert_ply_to_texture(input_ply_file, output_ply_file)
            print(f"Converted {input_ply_file} to {output_ply_file}")
