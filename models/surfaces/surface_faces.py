import random

import numpy as np
from skimage.filters import sato
from skimage.morphology import convex_hull_image
from skimage.segmentation import flood


def point_within_mask(mask):
    def sample_random_point(width, height):
        """
        Randomly samples a point from an image with given width and height.
        """
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        return (x, y)

    height, width = mask.shape

    random_pt = sample_random_point(width, height)
    while not mask[random_pt[1], random_pt[0]]:
        random_pt = sample_random_point(width, height)
    return random_pt


def mask_maker(image, mask_min, mask_max, stop_condition=12, max_fails=50, verbalize=False):
    chull = convex_hull_image(image)

    # Sato Ridge Operator
    result = sato(image, black_ridges=True, sigmas=[1])

    # Track percentage unfilled / unmasked
    unfilled_percentage = 100

    consecutive_fails = 0
    while (unfilled_percentage > stop_condition) and (
            consecutive_fails < max_fails):  # Generate a flood mask from random point
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

            consecutive_fails = 0
            yield flood_mask
        else:
            # Communicate
            if verbalize:
                print(f"Fail at: {flood_percentage}")

            consecutive_fails += 1

