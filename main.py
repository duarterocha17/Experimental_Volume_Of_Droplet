import os
from volume_calculation import Volume

im= Volume()
home_directory_name = '/Users/duarterocha17/Desktop/water' #directory containing 4 cases (4 main directories)
external_diameters = [0.0012, 0.0014, 0.00176, 0.00276] #external diameters for each case
main_directories_names = ['Water_nozzleCirc', 'Water_nozzleQuad', 'Water_nozzleTri', 'Water_nozzleCurv'] #names of main directories

for item in range(len(external_diameters)):
    main_directory_path = os.path.join(home_directory_name,main_directories_names[item])
    aux = im.loop_through_dir(main_directory_path, external_diameter_inlet = external_diameters[item])
