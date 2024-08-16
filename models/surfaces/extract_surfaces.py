import skimage
from surface_faces import mask_maker
import re
import os
import numpy as np
import csv

def mask_controller(filepath):
    img = skimage.io.imread(filepath)
    mask_gen = mask_maker(img,
                          mask_min=8, mask_max=78)
    yield from mask_gen


def directory_crawler(sample_directory):
    def extract_sample_name(filepath: str, pattern):
        file_str = filepath.replace("/", "+")  # makes regex easier to read
        match = re.search(pattern=pattern, string=file_str)
        yield filepath, str(f"{match.group(1)}_{match.group(2)}")

    # Specify the root directory to start the walk
    root_directory = str(f"data/{sample_directory}")
    print(root_directory)

    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(root_directory):
        # List all files in the current directory
        for filename in filenames:
            if ".DS_Store" not in filename:
                path = str(f"{os.path.join(dirpath, filename)}")
                yield from extract_sample_name(path, pattern=r"([^+]+)?\+([^+]+)?\.(png|jpg|jpeg)")


def setup_directory_writer(output_dir):
    def directory_writer(directory_path):
        while True:
            # ingest
            row_data = yield

            # write
            with open(directory_path, 'a', newline='') as directory_file:
                dir_fieldnames = ['original_file', 'sample_name', 'mask_filepath']
                dir_writer = csv.DictWriter(directory_file, fieldnames=fieldnames)
                dir_writer.writerow(row_data)

    filepath1 = str(f"{output_dir}/directory.csv")
    with open(filepath1, 'w', newline='') as csvfile:
        fieldnames = ['original_file', 'sample_name', 'mask_filepath']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    writer_generator = directory_writer(filepath1)
    writer_generator.__next__()
    return writer_generator


# makes a directory.csv file and a nested directory
# the subdirectory mask_data contains all .txt files with saved arrays
def mask_pipeline_controller(sample_directory, output_directory):
    # Change to the parent of the parent directory
    os.chdir(os.path.join(os.path.pardir, os.path.pardir))

    # make subdirectory to hold outputted masks
    os.mkdir(str(f"{output_directory}/mask_data"))

    # make csv directories
    pipeline_writer = setup_directory_writer(output_directory)

    crawler = directory_crawler(sample_directory)
    # crawl sample directory, generate masks for one sample at a time
    for filename, mask_file_prefix in crawler:
        # Instantiate surface separation pipeline for this mask
        sample_mask_generator = mask_controller(filename)

        mask_index = 0
        for new_mask in sample_mask_generator:
            # write mask to directory
            mask_save_filepath = str(f"{output_directory}/mask_data/{mask_file_prefix}_mask_{mask_index}.txt")
            np.savetxt(mask_save_filepath, new_mask)

            # record new file in directory
            pipeline_writer.send(
                {
                    "original_file": filename,
                    "sample_name": mask_file_prefix,
                    "mask_filepath": mask_save_filepath
                }
            )

            mask_index += 1

