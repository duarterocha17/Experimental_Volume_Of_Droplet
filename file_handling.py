import os
import numpy as np
import cv2 as cv

class File_Handling:
    
    def ch_dir(self, main_dir):
        
        #change directory
        os.chdir(main_dir)
        cur_dir = os.getcwd()

        return(cur_dir)

    def list_sub_dir(self, main_dir):

        #guarantee that you are in the correct directory
        cur_dir = self.ch_dir(main_dir)

        #list directories inside main directory, excluding files that start with '.'
        sub_dir = [filename for filename in os.listdir('.') if (not filename.startswith(".")) and (not filename.startswith("calibration")) and (not filename.startswith("results")) and (os.path.isdir(filename))]
        return(sub_dir)

    def clean_bin_image(self, image, lower_threshold = 50, upper_threshold = 255, flip = True):
        '''
        Analyse images in binary and eliminate unwanted reflections.
        '''
        
        ret,thresh = cv.threshold(image,lower_threshold,upper_threshold,cv.THRESH_BINARY) #set image to binary 

         #invert polarity and find contours
        des = cv.bitwise_not(thresh)
        contour,hier = cv.findContours(des,cv.RETR_CCOMP,cv.CHAIN_APPROX_SIMPLE) 

        #fill droplets (elimate refletions in droplets)
        for cnt in contour:
            cv.drawContours(des,[cnt],0,upper_threshold,-1)

        #flip image horizontally
        if flip:
            des = np.fliplr(des)

        return(des)


    def calibration(self, main_dir, external_diameter_inlet = 0.0012):
        '''
        Set new origin and convert pixels to meters based on inlet position and size.
        '''

        #guarantee that you are in the correct directory
        cur_dir = self.ch_dir(main_dir)

        #find path to the directory and image that starts with 'calibration'
        calibration_dir_path = os.path.join(cur_dir,[filename for filename in os.listdir('.') if filename.startswith("calibration")][0])
        calibration_im_path = os.path.join(calibration_dir_path,[filename for filename in os.listdir(calibration_dir_path) if filename.endswith(".tif")][0])

        #read calibration image
        calibration_im = cv.imread(calibration_im_path, 0)
        calibration_im = self.clean_bin_image(calibration_im)

        #set new origin
        y_aux = np.where(calibration_im[:,0] == 255)[0]
        y_origin = round((np.max(y_aux)-np.min(y_aux))/2+np.min(y_aux))
        x_aux = np.where(calibration_im[y_origin,:] == 255)[0]
        x_origin = round(np.max(x_aux)-np.min(x_aux))

        #convert pixels to meters
        inlet_y = np.where(calibration_im[:, x_origin-15:x_origin+15] == 255)[0] #+-15 px tolerance
        conv_px_m = external_diameter_inlet/(np.max(inlet_y)-np.min(inlet_y))

        #final calibrated image
        calibration_im = calibration_im[y_origin:,x_origin:]

        return(y_origin, x_origin, conv_px_m, calibration_im)

    def dic_im(self, main_dir):
        '''
        Create a dicionary with sub directories and absolute paths to images within.
        '''
        #guarantee that you are in the correct directory
        cur_dir = self.ch_dir(main_dir)
        
        #get path to all subdirectories in main directory, excluding calibration
        sub_dir_names = self.list_sub_dir(main_dir)

        #loop within the folder to create the dictionary with: 'key' = name of sub directory; 'value' = array with path to images
        dict = {}
        for sub_dir in sub_dir_names:
            path = os.path.join(cur_dir, sub_dir)
            path_im = []
            for file in os.listdir(path):
                if file.endswith(".tif"):
                    path_im.append(os.path.join(path, file))
            dict[sub_dir] = path_im
        
        return(dict)

