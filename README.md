# Experimental Volume Of Droplet

### About the project

This script was developed for a specific application within the scope of the project [*RheoOptimized2Dinks*](https://www.researchgate.net/project/Rheologically-optimized-2D-material-based-inks-RheoOptimized2Dinks), but it might be useful for fellow researchers. It is supposed to analyse and calculate the volume of the resulting droplets on a dripping or jetting nozzle, from the images taken in an experimental setup. 

The image below shows the output plotting of a detached droplet as a function of the internal inlet diameter. It is also shown the droplet's volume, as a function of the volume of a sphere with the internal inlet diameter.

![image](https://github.com/duarterocha17/Experimental_Volume_Of_Droplet/blob/main/water/Water_nozzleCirc/results/10uls_6400fps_b_C001H001S0001000195.png?raw=true)

>(10uls_6400fps_b_C001H001S0001000195) **V/V0 = 45.07**, measured in between z = 2.72 and z = 6.52.

---

### Requirements before use

This project was developed for a specific application and it was not tested for a large database. As such, it assumes several conditions, mainly concerning file organization:

* The files should be organized as it follows on the image below. A main directory (`Water_nozzleCirc`), associated to one unique calibration image, contains subdirectories, corresponding to:
    * Different measured flow rates (for instance, `1uls_6400fps_C001H001S0001` contains images of measurements done for a flow rate of 1 microliter per second), which are averaged by the results in the images within these folders. 
    * Calibration, which must start with the name `calibration`. It contains an unique image that is used to convert pixels to meters and to set the origin of the axis. This image shows the nozzle without any fluid and its position should correspond on the images within the other subdirectories, i.e., the apparatus position should remain steady while doing the measurements associated with a single calibration.
    * **No other subdirectory should be within the main directory**.

![image](https://github.com/duarterocha17/Experimental_Volume_Of_Droplet/blob/main/readme_image/files_organization.png?raw=true)

* **Only a few images**, containing enough information of the droplet's detachment, should be within the subdirectories.

* It is assumed that the both the nozzle and the camera were in a completely vertical position. 

* The images are assumed to have a `.tif` extension, but it can be adjusted simply by inputing an `extension` parameter, for example, `extension=".png"`, on the `Volume.loop_through_dir()` method. 

* In addiction, the images are 'cleaned' by first setting it to binary, which lower threshold can also be adjust by inputing an `lower_threshold` parameter, for example, `lower_threshold = 50`, on the `Volume.loop_through_dir()` method. If the image is too dark, the threshold should be lower and the opposite way around. 

* It uses the `numpy`, `matplotlib.pyplot` and `cv2` packages, which are assumed to be installed.

---

### How to use

To use this script, you simply need to insert the path to the main directory of your images in `main.py`.

```Python
from volume_calculation import Volume

im= Volume() #import Volume() class

main_directory = "insert directory path here" #path to main directory
im.loop_through_dir(main_directory, external_diameter_inlet = 0.0012,  diameter_inlet = 0.001, extension=".tif", lower_threshold=20) #adjust parameters accoding to your application
```

After calculation, the results will be stored in a created folder named `results`, within the main directory.

---

### Examples

`main.py` is adjusted to run on a loop for 4 different cases, corresponding to the 4 main directories `Water_nozzleCirc`, `Water_nozzleQuad`, `Water_nozzleTri` and `Water_nozzleCurv` (inside `water` folder), which have images associated to measurements on a circular, a square, a triangular and a curvilinear tringle nozzles, each with several flow rates measurements. 

Its results are stored in the `results` folder in each one of these main directories, which can be seen in this repository.

---

### Note

This is the 1st version of this script. It has only been tested for a small set of data, so any correction or suggestion is much appreciated!

######This work was financially supported by UIDP/00532/2020 (CEFT), funded by national funds through FCT/MCTES (PIDDAC); the developed
research is within the project’s scope PTDC/EME-APL/30765/2017-POCI-01-0145-FEDER-030765 (RheoOptimized2Dinks).
