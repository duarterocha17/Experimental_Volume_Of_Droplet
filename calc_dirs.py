from errno import ENXIO
import os
from unittest import result
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cv2 as cv
import math
import re
from pathlib import Path
from flood_fill import Flood_Fill
from file_handling import File_Handling
from volume_width import Volume_Width

#define functions to loop through directories

class Calculation:

    def calc_drop_flow_dir(self, path_flow_rate_dir, dict_flow_rate, conv_px_m, diameter_inlet = 0.001, factor_reduction = 1, lower_threshold = 20, upper_threshold = 255):

        '''
        Calculate the volume of droplet for each image in flow rate folder
        '''

        #call File_Handling object
        fh = File_Handling()
        vw = Volume_Width()

        #create array to store values
        results = []

        #get flow rate from dictionary
        str_files_name = list(dict_flow_rate)
        for file in str_files_name:
            if file.startswith('.'):
                str_files_name.remove(file)
        str_files_name = str_files_name[0]
        flow_rate = str_files_name[:re.search(r"\D+", str_files_name).start()]

        #get path of parent directory
        parent_path = Path(path_flow_rate_dir).parent.absolute()

        #create results folder in parent directory
        os.chdir(parent_path)
        if not os.path.isdir(os.path.join(parent_path, 'results')): 
            os.mkdir('results')

        #loop for every image in a flow rate folder
        for file in list(dict_flow_rate):
            if not file.startswith('.'):
                path_image = os.path.join(path_flow_rate_dir, file)
                im = cv.imread(path_image,0)
                im = fh.clean_bin_image(im, lower_threshold, upper_threshold) 
                y_origin = fh.set_origin_droplets(im) #readjust y origin
                im = im[y_origin:,:]
                im, factor_reduction = fh.reduce_size(im, factor_reduction)
                x = np.array(range(len(im[0])))*conv_px_m/diameter_inlet/factor_reduction
                y = np.array(range(len(im)))*conv_px_m/diameter_inlet/factor_reduction
                vw.representation(parent_path, im, x, y, file)
                islands, volume_drop, z_min, z_max, r_max = vw.volume(im, conv_px_m, diameter_inlet = diameter_inlet, factor_reduction = factor_reduction)
                results.append([flow_rate, volume_drop, z_min, z_max, r_max, islands])
        
        results = np.array(results)
        df = pd.DataFrame(results, columns=['flow_rate', 'volume', 'z_min', 'z_max', 'r_max', 'droplets'])

        return df

    def calc_jet_flow_rate(self, path_flow_rate_dir, dict_flow_rate, conv_px_m, diameter_inlet = 0.001, factor_reduction = 1, lower_threshold = 20, upper_threshold = 255):


        '''
        Calculate the width of jet for each image in flow rate folder
        '''

        #call File_Handling object
        fh = File_Handling()
        vw = Volume_Width()

        #create array to store values
        results = []

        #get flow rate from dictionary
        str_files_name = list(dict_flow_rate)[0]
        flow_rate = str_files_name[:re.search(r"\D+", str_files_name).start()]

        #get path of parent directory
        parent_path = Path(path_flow_rate_dir).parent.absolute()

        #create results folder in parent directory
        os.chdir(parent_path)
        if not os.path.isdir(os.path.join(parent_path, 'results')): 
            os.mkdir('results')

        #loop for every image in a flow rate folder
        for file in list(dict_flow_rate):
            if not file.startswith('.'):
                path_image = os.path.join(path_flow_rate_dir, file)
                im = cv.imread(path_image,0)
                x_origin = fh.set_origin_jet(im) #readjust x origin
                im = fh.clean_bin_image(im, lower_threshold, upper_threshold, droplet=False) 
                im = im[:,x_origin:]
                im, factor_reduction = fh.reduce_size(im, factor_reduction)
                x = np.array(range(len(im[0])))*conv_px_m/diameter_inlet/factor_reduction
                y = np.array(range(len(im)))*conv_px_m/diameter_inlet/factor_reduction
                vw.representation(parent_path, im, x, y, file)
                init_jet_width, jet_width_1d = vw.jet_width(im, conv_px_m, diameter_inlet, factor_reduction)
                results.append([flow_rate, init_jet_width, jet_width_1d])
        
        results = np.array(results)
        df = pd.DataFrame(results, columns=['flow_rate', 'initial_jet_width', 'jet_width_after_1Dlength'])

        return df

    def calc_nozzle_dir(self, path_nozzle_dir, dict_nozzle, droplet = True, external_diameter = 0.0012, diameter_inlet = 0.001, factor_reduction = 1, lower_threshold = 20, upper_threshold = 255):

        #call other classes
        fh = File_Handling()

        #change directory
        os.chdir(path_nozzle_dir)
        
        #get all subdirectories
        sub_directories = list(dict_nozzle.keys())

        #get calibration file
        conv_px_m = fh.calibration(path_nozzle_dir, external_diameter)

        #create empty array to store results
        results_df = pd.DataFrame()

        #find nozzle geometry in file name
        dir_name = os.path.basename(os.path.dirname(os.path.join(path_nozzle_dir, sub_directories[0])))
        nozzle_geometry = dir_name[dir_name.rfind('_')+1:]
        dry_wet_jet = dir_name[:dir_name.find('_')]

        #loop for every flow rate sub directories
        for sub_dir in sub_directories:
            if not (('calibration' in sub_dir) or ('results' in sub_dir)): 
                if not sub_dir.startswith('.'):
                    dict_flow_rate = dict_nozzle[sub_dir]
                    path_flow_rate = os.path.join(path_nozzle_dir, sub_dir)
                    if droplet:
                        results_df = results_df.append(self.calc_drop_flow_dir(path_flow_rate, dict_flow_rate, conv_px_m), ignore_index=True)
                    else:
                        results_df = results_df.append(self.calc_jet_flow_rate(path_flow_rate, dict_flow_rate, conv_px_m), ignore_index=True)

        #add wet or dry column in jet                
        if not droplet:
            dry_wet_jet_data = []
            for item in range(len(results_df)):
                dry_wet_jet_data.append(dry_wet_jet)
            results_df.insert(0,'wet_dry', dry_wet_jet_data)

        #insert nozzle name in dataframe
        nozzle_data = []
        for item in range(len(results_df)):
            nozzle_data.append(nozzle_geometry)
        results_df.insert(0,'nozzle', nozzle_data)
        
        return(results_df)

    def calc_fluid_dir(self, path_fluids, dict_fluids, dict_external_diameters, diameter_inlet = 0.001, factor_reduction = 1, lower_threshold = 20, upper_threshold = 255):
        
        #call other classes
        fh = File_Handling()
        
        #get all subdirectories
        sub_directories = list(dict_fluids.keys())

        #create empty array to store results
        results_droplet_df, results_jet_df = pd.DataFrame(), pd.DataFrame()

        for item in sub_directories:
            dict_nozzles = dict_fluids[item]

            #create a dataframe for the droplet analysis
            if item == 'droplet':
                if not os.path.isdir(os.path.join(os.path.join(path_fluids, item), 'results_droplet')): 
                    os.chdir(os.path.join(path_fluids,item))
                    os.mkdir('results_droplet')
                for nozzle in dict_nozzles.keys():
                    if not nozzle.startswith('result'):
                        path_nozzles = os.path.join(path_fluids, os.path.join(item, nozzle))
                        dict_nozzle = dict_nozzles[nozzle]
                        nozzle_name = nozzle[nozzle.rfind('_')+1:]
                        print(nozzle)
                        external_diameter = dict_external_diameters[nozzle_name]
                        results_droplet_df = results_droplet_df.append(self.calc_nozzle_dir(path_nozzles, dict_nozzle, external_diameter = external_diameter, diameter_inlet = 0.001, factor_reduction = 1, lower_threshold = 20, upper_threshold = 255))
                        
                results_dir = os.path.join(os.path.join(path_fluids, item), 'results_droplet')
                results_droplet_df.to_csv(os.path.join(results_dir, 'droplet_analysis.csv'))
            
            #create a dataframe for the jet analysis
            if item == 'jet':
                if not os.path.isdir(os.path.join(os.path.join(path_fluids, item), 'results_jet')): 
                    os.chdir(os.path.join(path_fluids,item))
                    os.mkdir('results_jet')
                for nozzle in dict_nozzles.keys():
                    if not nozzle.startswith('result'):
                        path_nozzles = os.path.join(path_fluids, os.path.join(item, nozzle))
                        dict_nozzle = dict_nozzles[nozzle]
                        nozzle_name = nozzle[nozzle.rfind('_')+1:]
                        print(nozzle)
                        external_diameter = dict_external_diameters[nozzle_name]
                        results_jet_df = results_jet_df.append(self.calc_nozzle_dir(path_nozzles, dict_nozzle, droplet=False, external_diameter = external_diameter, diameter_inlet = 0.001, factor_reduction = 1, lower_threshold = 20, upper_threshold = 255))
                results_dir = os.path.join(os.path.join(path_fluids, item), 'results_jet')
                results_jet_df.to_csv(os.path.join(results_dir, 'jet_analysis.csv'))
        return results_droplet_df, results_jet_df

    def calc_data_dir(self, main_dir, dict_external_diameters):
        
        file_handle = File_Handling()
        dict_files = file_handle.dict_dirs(main_dir)
        final_droplet_df, final_jet_df = pd.DataFrame(), pd.DataFrame()
        
        if not os.path.isdir(os.path.join(main_dir, 'results')): 
            os.chdir(main_dir)
            os.mkdir('results')

        for fluid in dict_files.keys():
            path_fluids = os.path.join(main_dir, fluid)
            dict_fluids = dict_files[fluid]
            df_droplets, df_jet = self.calc_fluid_dir(path_fluids, dict_fluids, dict_external_diameters, diameter_inlet = 0.001, factor_reduction = 1, lower_threshold = 20, upper_threshold = 255)
            droplet_data = []

            #add column with fluid
            for item_0 in range(len(df_droplets)):
                droplet_data.append(fluid)
            df_droplets.insert(0,'fluid', droplet_data)

            final_droplet_df = final_droplet_df.append(df_droplets)
        
        results_dir = os.path.join(main_dir, 'results')
        final_droplet_df.to_csv(os.path.join(results_dir, 'final_droplet_df.csv'))

        return final_droplet_df



calc = Calculation()
file_handle = File_Handling()
main_dir = '/Users/duarterocha17/Desktop/Experimental_Volume_Of_Droplet/data'
external_diameters = {'Circ': 0.0012, 'Quad': 0.0014, 'Tri': 0.00176, 'Curv': 0.00276}
df_droplets = calc.calc_data_dir(main_dir, external_diameters)
print(df_droplets)




