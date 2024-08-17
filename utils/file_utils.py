def which_shape(filepath):
    shape_names = ["polygon", "triangle", "circle", "square"]
    for shape in shape_names:
        if shape in filepath:
            return shape
    return "unknown"