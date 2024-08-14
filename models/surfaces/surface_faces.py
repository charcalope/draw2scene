import random

import matplotlib.pyplot as plt
import numpy as np
import skimage.io
from skimage.filters import sato
from skimage.morphology import convex_hull_image
from skimage.segmentation import flood, flood_fill


def sample_random_point(width, height):
    """
    Randomly samples a point from an image with given width and height.
    """
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    return x, y


def point_within_mask(mask):
    """
    :param mask: boolean mask array
    :return: (x,y) point within mask
    """
    height, width = mask.shape

    random_pt = sample_random_point(width, height)
    while not mask[random_pt[1], random_pt[0]]:
        random_pt = sample_random_point(width, height)
    return random_pt


def plot_image(img):
    # Plot the image
    plt.imshow(img, cmap='gray')
    plt.axis('off')  # Turn off axis labels
    plt.show()


def mask_maker(filepath, mask_min, mask_max, stop_condition=12, verbalize=False):
    """
    Generates a convex hull over the drawn shape in prepared sample
    Applies Sato ridge operator to create sufficient gradient
    Samples random points within mask, and attempts flood-fill

    If flood-fill area as % of convex hull area is in range (mask_min, mask_max)
    subtract mask area from convex hull, then yield mask

    Will stop independently if remaining % "stop_condition" is met

    :param filepath: image to load and process
    :param mask_min: min % to pass
    :param mask_max: max % to pass
    :param stop_condition: remaining % to stop iteration
    :param verbalize: communicate extra for debugging

    :return: generator yielding flood masks
    """
    # Load image and convex hull of drawn shape
    image = skimage.io.imread(filepath)
    chull = convex_hull_image(image)

    # Sato Ridge Operator
    result = sato(image, black_ridges=True, sigmas=[1])

    # Track percentage unfilled / unmasked
    unfilled_percentage = 100

    while unfilled_percentage > stop_condition:  # Generate a flood mask from random point
        random_pt = point_within_mask(chull)

        # Flood fill
        flood_mask = flood(result, (random_pt[1], random_pt[0]), tolerance=10, connectivity=1)

        # Remove parts of the flood mask that are not within the convex hull
        flood_mask = flood_mask & chull

        # Calculate the flood percentage within the convex hull
        flood_percentage = int(flood_mask.sum() / chull.sum() * 100)

        if verbalize:
            print(f"flood %: {flood_percentage} [{flood_mask.sum()} True]")
            print(f"  shape: {flood_mask.shape}")
            print(f"chull has len {len(chull)} [{chull.sum()} True]")
            print(f"  shape: {chull.shape}")

        # Compare to threshold
        if flood_percentage in range(mask_min, mask_max):
            # Cut out the new mask from the convex hull
            chull = np.logical_and(chull, ~flood_mask)

            # Update percentages
            unfilled_percentage -= flood_percentage

            # Communicate
            if verbalize:
                print(f"Pass at: {flood_percentage}")
                plot_image(flood_fill(result, (random_pt[1], random_pt[0]), new_value=110, tolerance=10))

            yield flood_mask
        else:
            # Communicate
            if verbalize:
                print(f"Fail at: {flood_percentage}")
            yield


def mask_controller(filepath, img_output=False):
    """
    Runs generator mask_gen
    Tracks consecutive fails, stops iteration at 50

    Creates an image copy, recolors with flood fill from masks
    Returns this along with metadata on mask count, coloring used

    :param filepath: image to process
    :param img_output: returns image only, or None if no masks generated
    :return: image and metadata
    """
    mask_gen = mask_maker(filepath,
                          mask_min=11, mask_max=78)

    masks = []
    consecutive_fails = 0
    while consecutive_fails < 50:
        try:
            response = mask_gen.__next__()
            if response is not None:  # success, is a mask
                consecutive_fails = 0
                masks.append(response)
            else:
                consecutive_fails += 1  # fail
        except StopIteration:
            exit()

    img = skimage.io.imread(filepath)

    # Create a copy of the image to modify
    recolored_img = img.copy()
    secondary_colors = []

    # Sort masks by area (count of True pixels)
    masks.sort(key=lambda m: np.sum(m), reverse=True)

    # Recolor the largest mask in red and the others randomly
    for i, m in enumerate(masks):
        if i == 0:
            # Largest mask, color it red
            color = np.array([255, 0, 0], dtype=np.uint8)
        else:
            # Other masks, color them randomly
            color = np.random.randint(0, 256, size=(3,), dtype=np.uint8)
            secondary_colors.append(color)

        # If the image is grayscale, convert to RGB
        if len(recolored_img.shape) == 2:  # grayscale image
            recolored_img = np.stack([recolored_img] * 3, axis=-1)

        # Apply the color to the mask region in the image
        recolored_img[m] = color

    if img_output:  # do not return metadata with image
        if len(masks) == 0:
            return None
        else:
            return recolored_img

    # return results
    if len(masks) > 0:
        return {
            "status": "pass",
            "original_file": filepath,
            "masks_n": len(masks),
            "primary_color": [255,0,0],
            "secondary_colors": secondary_colors,
        }
    else:
        return {
            "status": "fail",
            "original_file": filepath,
        }


