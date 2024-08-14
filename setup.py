def check_requirements():
    try:
        import skimage
        import numpy
        import pandas
        import matplotlib
        import sklearn
    except ImportError:
        print("Required packages not installed.")
        print("Try: pip install requirements.txt")