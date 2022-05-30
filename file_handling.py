from curses.ascii import isalnum
from fileinput import filename
import os
import numpy as np
import cv2 as cv
from pip import main
from flood_fill import Flood_Fill

class File_Handling:

    '''
    Files are organized in directories as Data->Fluids->Jet/Droplet->Nozzle->Flow_Rate->Images
    '''

    def dict_dirs(self, main_dir):
        '''
        Create dictionary with all folders and subfolders of main data directory
        '''

        if os.path.isdir(main_dir):
            dict_var = {}
            for name in os.listdir(main_dir):
                 dict_var[name] = self.dict_dirs(os.path.join(main_dir, name))
        else:
            dict_var = os.path.getsize(main_dir)
        return dict_var

    def clean_bin_image(self, image, lower_threshold = 20, upper_threshold = 255, flip = True, droplet = True):
        '''
        Analyse images in binary and eliminate unwanted reflections.
        '''
        
        ret,thresh = cv.threshold(image,lower_threshold,upper_threshold,cv.THRESH_BINARY) #set image to binary 

        #invert polarity and find contours
        des = cv.bitwise_not(thresh)

        #if jet, turn last cells to fluid before fixing reflections
        if not droplet:
            last_column = np.argwhere(des[:,0] == 255)
            for row in range(len(des)):
                if (row < np.max(last_column[:,0]-10) and row > np.min(last_column[:,0]+10)):
                    des[row,0] = 255

        contour,hier = cv.findContours(des,cv.RETR_CCOMP,cv.CHAIN_APPROX_SIMPLE) 

        #fill droplets (elimate refletions in droplets)
        for cnt in contour:
            cv.drawContours(des,[cnt],0,upper_threshold,-1)

        #flip image horizontally
        if flip:
            des = np.fliplr(des)

        return(des)


    def calibration(self, test_dir, external_diameter_inlet = 0.0012):
        '''
        Set new origin and convert pixels to meters based on inlet position and size.
        '''

        #test directory contains a single calibration image
        os.chdir(test_dir)
        cur_dir = os.getcwd()

        #find path to the directory and image that starts with 'calibration'
        calibration_dir_path = os.path.join(cur_dir,[filename for filename in os.listdir('.') if filename.startswith("calibration")][0])
        calibration_im_path = os.path.join(calibration_dir_path,[filename for filename in os.listdir(calibration_dir_path) if filename.endswith(".tif")][0])

        #read calibration image
        calibration_im = cv.imread(calibration_im_path, 0)
        calibration_im = self.clean_bin_image(calibration_im)

        #set new origin
        y_aux = np.argwhere(calibration_im == 255)[:,0]
        y_origin = round((np.mean(y_aux)))
        x_aux = np.argwhere(calibration_im[y_origin,:] == 255)
        x_origin = round(np.max(x_aux)-np.min(x_aux))

        #convert pixels to meters
        inlet_y = np.argwhere(calibration_im[:, x_origin-5:x_origin+5] == 255)[:,0] #+-5 px tolerance
        conv_px_m = external_diameter_inlet/(np.max(inlet_y)-np.min(inlet_y))

        return(conv_px_m)
    
    def set_origin_droplets(self, im):
        
        #set y origin again in case position was slightly altered
        y_aux = np.argwhere(im == 255)[:,0]
        y_origin = round(np.mean(y_aux))
        
        return(y_origin)

    def set_origin_jet(self, init_im, lower_threshold = 20, upper_threshold = 255, flip = True):

        #set image to binary 
        ret,thresh = cv.threshold(init_im,lower_threshold,upper_threshold,cv.THRESH_BINARY)

        #invert polarity and find contours
        des = cv.bitwise_not(thresh)

        #flip image horizontally
        if flip:
            des = np.fliplr(des)

        #set x origin
        y_origin = round(np.mean(np.argwhere(des == 255)[:,0]))
        filtered_lines = np.argwhere(des[y_origin-5:y_origin+5,:] == 0)
        x_origin = np.min(filtered_lines[:,1])

        
        return(x_origin)

    def reduce_size(self, im, factor_reduction = 1):
    
        '''
        If there are a lot of images, it might be necessary to reduce size to run the 
        script in a reasonable time.
        '''

        # percent of original size
        width = int(im.shape[1] * factor_reduction)
        height = int(im.shape[0] *  factor_reduction)
        dim = (width, height)
        
        # resize image
        resized = cv.resize(im, dim, interpolation = cv.INTER_AREA)
        
        return(resized, factor_reduction)
