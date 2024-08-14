import os
import numpy
import pandas as pd
from models.clustering.image_processing_pipeline import canny_hough_xtion_dbscan_pipeline, graph_over_image


def pad(final_length):
    """
    helps ensure array is evenly sized for casting to numpy array
    """
    return lambda short_array: short_array + [[0,0] for i in range(len(short_array), final_length)]

def apply_pipeline(pipeline=canny_hough_xtion_dbscan_pipeline, debug=False):
    """
    Applies point-centric pipeline to small dataset "/data/sample_drawn_shapes"
    Displays model output, asks user to label surface count
    Saves model outputs and labels to csv file

    :param pipeline: function producing points and centroids, such as the default
    :param debug: extra verbalization
    """
    # Record all data
    training_data = dict()
    training_data["filename"] = []
    training_data["centroids"] = []
    training_data["all_points"] = []
    training_data["combined_point_arrays"] = []
    training_data["labels"] = []

    # Establish required shape of final array
    max_centroid_length = 0
    max_points_length = 0

    # Iterate through sample data and apply pipeline
    files = os.listdir("../../data/sample_drawn_shapes")
    for f in files:
        full_path = str(f"data/sample_drawn_shapes/{f}")
        centroid_xs, centroid_ys, x_coords, y_coords = pipeline(full_path)
        centroids, points = (list(zip(centroid_xs, centroid_ys)), list(zip(x_coords, y_coords)))

        # check for new maximums
        max_centroid_length = max(max_centroid_length, len(centroids))
        max_points_length = max(max_points_length, len(points))

        # add to training data
        training_data["filename"].append(full_path)
        training_data["centroids"].append(centroids)
        training_data["all_points"].append(points)

        if debug:
            surface_count_label = -1
        else:
            # Display image, intersection points and centroids
            graph_over_image(full_path, centroid_xs, centroid_ys, x_coords, y_coords)

            # Get input from user
            surface_count_label = input("surfaces visible = ")
            try:
                surface_count_label = int(surface_count_label)
            # Handle invalid non-integer string
            except ValueError:
                try:
                    # Warn the user then re-attempt
                    print("Final chance to try again before you lose your data. Enter a single integer, like: 0")
                    surface_count_label = input("surfaces visible = ")
                    surface_count_label = int(surface_count_label)
                    continue  # possibly unnecessary?
                except ValueError:
                    print("Invalid input, exiting program.")
                    return

        training_data["labels"].append(surface_count_label)

    # Define padding function with longest array length seen
    padding = pad(final_length=max(max_points_length, max_centroid_length))

    # Combine Centroid and Point arrays into single array: [point array, centroid array]
    combiner = zip(training_data["all_points"], training_data["centroids"])

    for pts, cents in combiner:
        combined_array = numpy.array([padding(pts), padding(cents)])
        training_data["combined_point_arrays"].append(combined_array)

    df_data = dict()
    df_data["filename"] = training_data["filename"]
    df_data["combined_point_arrays"] = training_data["combined_point_arrays"]
    df_data["labels"] = training_data["labels"]

    # Create dataframe and write to file
    df = pd.DataFrame.from_dict(df_data)
    df.to_csv("data/sample2point_pipeline_results.csv")

