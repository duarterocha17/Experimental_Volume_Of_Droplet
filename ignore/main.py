import os

from pip import main
from volume_width import Volume_Width
import cv2 as cv
from file_handling import File_Handling

im= Volume_Width()

#CHANGE NAME OF home_directory_name TO FOLDER WITH MAIN DIRECTORIES
water_directory_name = '/Users/duarterocha17/Desktop/Experimental_Volume_Of_Droplet/data/water' #directory containing 4 cases (4 main directories)
external_diameters = [0.0012, 0.0014, 0.00176, 0.00276] #external diameters for each case
main_directories_names = ['Water_nozzleCirc', 'Water_nozzleQuad', 'Water_nozzleTri', 'Water_nozzleCurv'] #names of main directories

for item in range(len(external_diameters)):
    main_directory_path = os.path.join(water_directory_name,main_directories_names[item])
    aux = im.loop_through_dir(main_directory_path, external_diameter_inlet = external_diameters[item], extension=".tif", lower_threshold=20)
