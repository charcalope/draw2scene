import os
import skimage
from standardize_img_shape import run_convex_hull

# Ingests filepath of raw image scan, applies processing pipeline, then saves with integer index suffix
# destination_filepath_prefix should be path from top level directory to folder for processed samples
#   i.e. "data/samples/triangles" with no trailing slash
def apply_pipe_save(destination_filepath_prefix):
    i = 0
    while True:
        raw_filepath = yield
        cropped_image = run_convex_hull(raw_filepath)
        image = skimage.util.img_as_ubyte(cropped_image)
        skimage.io.imsave(str(f"{destination_filepath_prefix}/sample_{i}.png"), image)
        i += 1


# applies pipeline to all files in given directory
def run_pipeline_all(origin_dir_path, final_dir_path):
    if final_dir_path[-1] == "/":
        final_dir_path = final_dir_path.strip("/")

    # create coroutine and make ready
    pipe_sink = apply_pipe_save(final_dir_path)
    pipe_sink.__next__()

    # iterate through directory of raw scans
    file_list = os.listdir(origin_dir_path)
    for path in file_list:
        pipe_sink.send(str(f"{origin_dir_path}/{path}"))


# example usage
run_pipeline_all("../data/raw_scans/Squares/", "../data/sample_set_2/square_face")
run_pipeline_all("../data/raw_scans/Triangles/", "../data/sample_set_2/triangle_face")
run_pipeline_all("../data/raw_scans/Polygons/", "../data/sample_set_2/polygon_face")
run_pipeline_all("../data/raw_scans/Circles/", "../data/sample_set_2/circle_face")
