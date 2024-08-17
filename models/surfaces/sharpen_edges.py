import os

import numpy as np
import pandas as pd
import skimage.io
from skimage.draw import polygon_perimeter
from skimage.feature import corner_harris, corner_peaks
from skimage.morphology import convex_hull_image


def sharpen_mask(mask_arr):
    # estimate corners
    trail_coords = corner_peaks(corner_harris(mask_arr), min_distance=5, threshold_rel=0.01)
    rrs = [p[0] for p in trail_coords]
    ccs = [p[1] for p in trail_coords]

    # create a polygon
    r, c = polygon_perimeter(rrs, ccs)
    rr, cc = skimage.draw.polygon(r, c)
    img = np.zeros((128, 128), dtype=int)
    img[rr, cc] = 1

    # apply convex hull
    chull = convex_hull_image(img)
    return chull


def apply_sharpen_save(directory_file, save_directory, display=False):
    # Change to the parent of the parent directory
    os.chdir(os.path.join(os.path.pardir, os.path.pardir))

    # load file locations
    df = pd.read_csv(directory_file)

    # apply pipeline to linear shapes only
    df = df[df["shape"] != "polygon"]
    df = df[df["shape"] != "circle"]

    image_files = df["original_file"]
    mask_files = df["mask_filepath"]

    for mask in mask_files:
        # load mask
        arr = np.loadtxt(mask)
        try:
            # sharpen
            sharpened_mask = sharpen_mask(arr)
            # save
            new_filepath = save_directory + "/" + mask.split("/").pop().replace(".txt", "_sharp.txt")
            np.savetxt(new_filepath, sharpened_mask)
        except IndexError:
            # TODO: investigate following error
            # IndexError: list index out of range
            # poly_clipped = poly.clip_to_bbox(clip_rect).to_polygons()[0]
            print(f"Error, sample {mask} failed")


