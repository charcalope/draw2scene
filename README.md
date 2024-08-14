# draw2scene
working on algorithms to support estimation &amp; rendering of handrawn shapes to 3D interpretations



### Datasets
There are two datasets of handrawn shapes, processed from raw scans, and ready for use. All scanned from my iPhone, drawn with variations, features intended to be challening for models like unclosed polygons, and at varying scales.

| Location | Description |
| --- | --- |
| data/sample_drawn_shapes | small # of samples, unsorted, mostly cubes |
| data/sample_set_2 | larger dataset of samples (~150) sorted by shape of primary face: square, circle, triangle, polygon |

Under dataset_prep, there is code for preparing raw image scans for 

### Working on
**Surface Separation**

<img src="https://github.com/user-attachments/assets/b3ae03f8-e4aa-4fbc-a3fa-3abade828334" width="250" height="250">


**Up Next**

1. Ensuring robustness with polygon surfaces, handling failure cases
2. Implementing an approach to extrusion from surfaces [3D interpretation]
3. Build out first foundations for "scene-building"
    - 3D representations of model outputs
    - Define search space for camera poses


