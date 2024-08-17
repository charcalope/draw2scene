import numpy as np
import skimage
import matplotlib.pyplot as plt
import pandas as pd
import os
import csv
from utils.terminal_utils import up_down_selection


def setup_label_writer(output_dir):
    def label_writer(directory_path):
        while True:
            # ingest
            row_data = yield

            # write
            with open(directory_path, 'a', newline='') as directory_file:
                dir_fieldnames = ['mask_filepath', 'label']
                dir_writer = csv.DictWriter(directory_file, fieldnames=dir_fieldnames)
                dir_writer.writerow(row_data)

    if not os.path.exists(output_dir):
        with open(output_dir, 'w', newline='') as csvfile:
            fieldnames = ['mask_filepath', 'label']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    writer_generator = label_writer(output_dir)
    writer_generator.__next__()
    return writer_generator


def display_each_mask(directory_file, label_destination):
    # Change to the parent of the parent directory
    os.chdir(os.path.join(os.path.pardir, os.path.pardir))

    # Setup label writer
    label_writer = setup_label_writer(label_destination)

    labeled_masks = []
    # check for existing labels, possible prior session of labeling
    if os.path.exists(label_destination):
        print("prior labeling data found...")
        df2 = pd.read_csv(label_destination)
        labeled_masks = list(df2["mask_filepath"])

    # load file locations
    df = pd.read_csv(directory_file)
    image_files = df["original_file"]
    mask_files = df["mask_filepath"]

    for image, mask in zip(image_files, mask_files):
        if mask not in labeled_masks:
            # load mask and image
            arr = np.loadtxt(mask)

            # resize and overwrite
            resized_array = skimage.transform.resize(arr, (128, 128))
            np.savetxt(mask, resized_array)

            img = skimage.io.imread(image)

            # display to user
            plt.imshow(img)
            plt.imshow(arr, alpha=0.4)
            plt.show()

            # allow labeling with terminal interface
            user_label = up_down_selection(choices=[
                "multiple surfaces",
                "single surface",
                "edge",
                "convex hull artifact",
                "preprocessing / scan failure"
            ])

            label_writer.send({
                "mask_filepath": mask,
                "label": user_label
            })
        else:
            print("skipping mask labeled in prior session...")

