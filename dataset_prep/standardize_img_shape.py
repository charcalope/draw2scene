
# returns a cropped image bounded at the max height/width of the convex hull
def crop_to_convex_hull(original, chull, margin=0):
    import numpy as np
    orig_row_max, orig_col_max = np.shape(original)
    [rows, columns] = np.where(chull)
    row1 = min(rows)
    row2 = max(rows)
    col1 = min(columns)
    col2 = max(columns)

    # add margin
    if margin > 0:
        if (row1 - margin) >= 0:
            row1 = row1 - margin
        if (row2 + margin) <= orig_row_max:
            row2 = row2 + margin
        if (col1 - margin) >= 0:
            col1 = col1 - margin
        if (col2 + margin) <= orig_col_max:
            col2 = col2 + margin
    cropped_image = original[row1:row2, col1:col2]
    return cropped_image


# loads raw scan from filepath, filters and crops, returns image as object
def run_convex_hull(filepath, debug=False):
    import matplotlib.pyplot as plt

    from skimage.morphology import convex_hull_image
    from skimage import feature

    from skimage import io, filters
    from skimage.color import rgba2rgb, rgb2gray
    # Load the image
    image = io.imread(filepath)
    image = rgb2gray(rgba2rgb(image))

    # CANNY
    # Compute the Canny filter for two values of sigma
    edges1 = feature.canny(image)
    edges2 = feature.canny(image, sigma=3)

    image = edges2
    chull = convex_hull_image(image)
    cropped_image = crop_to_convex_hull(image, chull, margin=15)
    return cropped_image
