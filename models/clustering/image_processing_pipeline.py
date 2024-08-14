def calculate_centroid(points):
    """
    Calculate the centroid of a given set of points.

    Args:
        points (list of tuples): List of (x, y) coordinate tuples.

    Returns:
        tuple: Centroid coordinates (x_centroid, y_centroid).
    """
    if points is None or len(points) == 0:
        return (0, 0)

    n = len(points)
    x_coords = [point[0] for point in points]
    y_coords = [point[1] for point in points]

    x_centroid = sum(x_coords) / n
    y_centroid = sum(y_coords) / n

    return (x_centroid, y_centroid)


def cluster_points(points, eps=5, min_samples=2):
    """
    Clusters the given points
    :param points: array of (x,y) tuples

    dbscan parameters
    :param eps:
    :param min_samples:

    :return: clustered_points
    """
    from sklearn.cluster import DBSCAN
    import numpy as np

    if len(points) == 0:
        return []

    # Convert list of tuples to numpy array for DBSCAN
    points_array = np.array(points)

    # Apply DBSCAN clustering
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(points_array)
    labels = db.labels_

    # Extract clustered points
    clustered_points = [points_array[labels == i] for i in range(max(labels) + 1) if i != -1]

    return clustered_points


def filter_points_within_bounds(points, image_shape):
    # Filters out points that lie outside the bounds of the original image.
    height, width = image_shape
    filtered_points = [(x, y) for x, y in points if 0 <= x < width and 0 <= y < height]
    return filtered_points


def canny_hough_xtion_dbscan_pipeline(image):
    """
    For a given, loaded image object
    Applies Canny, Hough, Line Intersection, and clustering

    Returns points and point cluster centroids in order:
    (centroid_xs, centroid_ys, x_coords, y_coords)
    """
    import numpy as np
    from skimage.transform import hough_line, hough_line_peaks
    from skimage import feature
    from skimage import io
    from skimage.color import rgba2rgb, rgb2gray

    def calculate_intersections(lines):
        intersections = []
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                (rho1, theta1) = lines[i]
                (rho2, theta2) = lines[j]
                A = np.array([
                    [np.cos(theta1), np.sin(theta1)],
                    [np.cos(theta2), np.sin(theta2)]
                ])
                b = np.array([rho1, rho2])
                if np.linalg.det(A) != 0:  # Check if lines are not parallel
                    intersection = np.linalg.solve(A, b)
                    intersections.append(intersection)
        return np.array(intersections)

    im_shape = image.shape[:2]

    # CANNY
    # Compute the Canny filter for two values of sigma
    edges1 = feature.canny(image)

    # HOUGH
    # Classic straight-line Hough transform
    # Set a precision of 0.5 degree.
    tested_angles = np.linspace(-np.pi / 2, np.pi / 2, 150, endpoint=False)
    h, theta, d = hough_line(edges1, theta=tested_angles)

    # Extract lines
    lines = []
    for _, angle, dist in zip(*hough_line_peaks(h, theta, d)):
        lines.append((dist, angle))

    # Calculate intersections
    intersections = calculate_intersections(lines)

    # Convert intersections to coordinates on the image plane
    x_coords = [int(x) for x in list(intersections[:, 0])]
    y_coords = [int(x) for x in list(intersections[:, 1])]

    # Filter to bounds of original image
    # otherwise shape will look like it disappeared - its just tiny
    filtered_points = filter_points_within_bounds(zip(x_coords, y_coords), im_shape)

    # unzip points
    x_coords = [p[0] for p in filtered_points]
    y_coords = [p[1] for p in filtered_points]

    # cluster points, then calculate centroid
    centroid_xs = []
    centroid_ys = []

    # cluster points
    clustered_points = cluster_points(points=filtered_points)
    for i, cluster in enumerate(clustered_points):
        central_pt = calculate_centroid(cluster)
        centroid_xs.append(int(central_pt[0]))
        centroid_ys.append(int(central_pt[1]))

    return centroid_xs, centroid_ys, x_coords, y_coords


# Graphs points and centroids over image in filepath
def graph_over_image(filepath, centroid_xs, centroid_ys, x_coords, y_coords):
    import matplotlib.pyplot as plt

    im = plt.imread(filepath)
    implot = plt.imshow(im)

    # plot filtered intersection points in red
    plt.scatter(x=x_coords, y=y_coords, c='r')

    # plot cluster centroid points in blue
    plt.scatter(x=centroid_xs, y=centroid_ys, c='b')
    plt.show()
