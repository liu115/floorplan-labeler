# Floorplan labeling tool

## Requirements
* python >= 3.7
* PyQt5
* numpy
* plyfile

## How to run and use?
```
python app.py PLY_DATA_DIR
```
This will read all `.ply` files in `PLY_DATA_DIR`.
Currently, it will save result in `.json` with same name as the file in `PLY_DATA_DIR`.

1. Click point cloud to label corners
2. `W`, `A`, `S`, `D` to move point cloud 
3. `E`, `R` to rotate point cloud
4. Scroll from zoom in and out
5. Click `room` or `axis` button on bottom right to switch labeling mode
6. Click `save` button to save result
7. `P`: previous scene. `N`: next scene
8. The bottom panel shows the height and thickness for the two slice. Users can adjust the values to view the different slice from the  projection.
