# Experimental Volume Of Droplet

### About the project

The project was developed for a personal application, but it might be useful for fellow researchers. It is supposed to analyse and calculate the volume of the resulting droplets on a dripping or jetting nozzle, from the images taken in an experimental setup. 

The image below shows the output plotting of a detached droplet, as a function of the internal inlet diameter. It is also shown the droplet's volume, as a function of the volume of a sphere with the internal inlet diameter.

![image](https://github.com/duarterocha17/Experimental_Volume_Of_Droplet/blob/main/water/Water_nozzleCirc/results/10uls_6400fps_b_C001H001S0001000195.png?raw=true)

>(10uls_6400fps_b_C001H001S0001000195) **V/V0 = 45.07**, measured in between z = 2.72 and z = 6.52.

---

### Requirements before use

This project was developed for a specific application and it was not tested for a large database. As such, it assumes several conditions, mainly concerning files organization:

* The files should be organized as it follows on the image below. A main directory (`Water_nozzleCirc`), associated to one unique calibration image, contains subdirectories, corresponding to:
    * Different measured flow rates (for instance, `1uls_6400fps_C001H001S0001` contains images of measurements done for a flow rate of 1 microliter per second), which are averaged by the results in the images within this folders. 
    * Calibration, which must start with the name `calibration`. It contains an unique image that is used to convert pixels to meters and to set the origin of the axis. This image shows the nozzle without any fluid and its position should correspond to that on the images within the other subdirectories, i.e., the apparatus position should remain steady while doing the measurements associated with a single calibration.
    * **No other subdirectory should be within the main directory**.

![image](https://github.com/duarterocha17/Experimental_Volume_Of_Droplet/blob/main/readme_image/files_organization.png?raw=true)

* **Only a few images**, containing enough information of the droplet's detachment, should be within the subdirectories.

* It is assumed that the both the nozzle and the camera were in a completely vertical position. 

* The images are assumed to with a `.tif` extension, but it can be adjusted simply by inputing an `extension` parameter, for example, `extension=".png"`, on the `Volume.loop_through_dir()` method. 

* In addiction, the images are 'cleaned' by first setting it to binary, which lower threshold can also be adjust by inputing an `lower_threshold` parameter, for example, `lower_threshold = 50`, on the `Volume.loop_through_dir()` method. If the image is too dark, the threshold should be lower and the opposite way around. 

---

### How to use

For staters, 

### Examples


###### Assumed images are .tif 
