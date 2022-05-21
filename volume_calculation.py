import os
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
import math
from flood_fill import Flood_Fill
from file_handling import File_Handling

class Volume:

    def call_flood_fill(self):
        #call class Flood_Fill
        self.ff = Flood_Fill()
    
    def call_file_handling(self):
        #call class File_Handling
        self.fh = File_Handling()

    def representation(self, main_dir, im, x, y, name_subdir):

        '''
        Represent image as a function of the internal diameter.
        '''

        #import File_Handling class
        self.call_file_handling()

        #represent image
        x_grid,y_grid = np.meshgrid(x,y)
        fig, ax = plt.subplots(figsize = (np.max(x)*2, np.max(y)*2))
        ax.contourf(x_grid,y_grid,im, origin='lower', cmap = 'Greys')

        #add labels
        ax.set_ylabel('$R/D_0$', fontname="Helvetica", fontsize=30)
        ax.set_yticks(range(0,round(np.max(y)),1))
        ax.set_yticklabels(range(0,round(np.max(y)),1), fontname="Helvetica", fontsize=30)
        ax.set_xlabel('$L/D_0$', fontname="Helvetica", fontsize=30)
        ax.set_xticks(range(0,round(np.max(x)),1))
        ax.set_xticklabels(range(0,round(np.max(x)),1), fontname="Helvetica", fontsize=30) 

        #save image in results subdirectory
        print(str(name_subdir))
        fig.savefig(os.path.join(main_dir, 'results/' + str(name_subdir)),bbox_inches='tight', dpi=150)
        plt.close('all')


    def droplets_domain_dict(self, matrix, diameter_inlet, neighbors, conv_px_m ,factor_reduction = 1):
        '''
        Method to isolate the nodes of each droplet.
        '''
        
        #import Flood_Fill class
        self.call_flood_fill()

        islands = 0
        all_droplets = {}
        m = np.copy(np.array(matrix, np.int32))
        filtered_matrix = np.where(m == 255)

        #run flood fill for each droplet
        while len(filtered_matrix[0])>0:
            point = (filtered_matrix[0][0], filtered_matrix[1][0])
            if self.ff.is_fluid(m,point):
                self.ff.flood_fill(point, m, all_droplets, neighbors, islands)  
                islands += 1
            filtered_matrix = np.where(m == 255)
        
        #remove satellite droplets from list of droplets
        all_droplets.pop(0)
        for row in range(1, islands):
            droplet_row = np.array(all_droplets[row])

            #remove droplet if it has no nodes
            if droplet_row.size == 0:
                islands -= 1
                all_droplets.pop(row)

            #remove droplet if it is shorter than 2/3D in x or 1/3D in y  
            else:
                if (((np.max(droplet_row[:,0]) - np.min(droplet_row[:,0]))*conv_px_m/diameter_inlet/factor_reduction <= 2/3) or 
                ((np.max(droplet_row[:,1]) - np.min(droplet_row[:,1]))*conv_px_m/diameter_inlet/factor_reduction <= 1/3)):
                    islands -= 1
                    all_droplets.pop(row)

        return(islands, all_droplets)  

    def volume(self, im, conv_px_m, diameter_inlet = 0.001, factor_reduction = 1):

        '''
        Calculate volume of first non-satellite detached droplet.
        '''

        #import Flood_Fill class
        self.call_flood_fill()

        #get domain of first detached droplet
        neighbors = self.ff.neighbors_dict(im)
        islands, all_droplets = self.droplets_domain_dict(im, diameter_inlet, neighbors, conv_px_m, factor_reduction)
        first_detached_droplet = np.array(all_droplets[list(all_droplets.keys())[0]])
        
        #integrate for droplet's length 
        volume_single_droplet = 0

        for x_value in np.unique(first_detached_droplet[:,1]):
            mask = (first_detached_droplet[:, 1] == x_value)
            y_list = first_detached_droplet[mask, :][:,0]
            y_radius = (np.max(y_list)-np.min(y_list))*conv_px_m/factor_reduction
            dx = conv_px_m/factor_reduction
            volume_single_droplet += dx*(y_radius**2*math.pi)
        
        #get volume as dimensionless variable
        volume_single_droplet = round(volume_single_droplet/(4/3*math.pi*(diameter_inlet/2)**3),2)

        #show x domain of the droplet
        x_min = round(np.min(first_detached_droplet[:,1])*conv_px_m/factor_reduction/diameter_inlet,2)
        x_max = round(np.max(first_detached_droplet[:,1])*conv_px_m/factor_reduction/diameter_inlet,2)

        return(islands, volume_single_droplet, x_min, x_max)   

    
    def loop_through_dir(self, main_dir, external_diameter_inlet = 0.0012, diameter_inlet = 0.001):

        '''
        Loop volume and representation function through files in directory
        '''

        #import classes
        self.call_file_handling()
        self.call_flood_fill()

        #guarantee that you are in the correct directory
        cur_dir = self.fh.ch_dir(main_dir)

        #create directory to save files
        if not os.path.isdir('results'): 
            os.mkdir('results')

        #get path to all subdirectories in main directory, excluding calibration
        sub_dir_names = self.fh.list_sub_dir(main_dir)
        dict_images = self.fh.dic_im(main_dir)

        #values from calibration
        y_origin, x_origin, conv_px_m, calibration_im = self.fh.calibration(main_dir, external_diameter_inlet)

        #for each directory with images
        for dir in sub_dir_names:
            if os.path.exists(os.path.join(cur_dir,'results/' + str(dir) + '.txt')):
                os.remove(os.path.join(cur_dir,'results/' + str(dir) + '.txt'))

            #read each image in each subdirectory
            volume_drops = []
            for path in dict_images[dir]:
                im = cv.imread(path,0)
                im = self.fh.clean_bin_image(im) 
                y_origin = self.fh.double_calibration(im) #readjust y origin
                im = im[y_origin:,:]
                im, factor_reduction = self.ff.reduce_size(im,1)
                x = np.array(range(len(im[0])))*conv_px_m/diameter_inlet/factor_reduction
                y = np.array(range(len(im)))*conv_px_m/diameter_inlet/factor_reduction
                self.representation(main_dir, im, x, y, path[path.rfind("/")+1:path.rfind(".")])
                islands, volume_drop, z_min, z_max = self.volume(im, conv_px_m, diameter_inlet = 0.001, factor_reduction = 1)
                volume_drops.append(volume_drop)

                #save results in txt file
                file_object = open(os.path.join(cur_dir,'results/' + str(dir) + '.txt'), 'a')
                file_object.write('(' + str(path[path.rfind("/")+1:path.rfind(".")]) + ') V/V0 = ' + str(volume_drop) + ', measured in between z = ' + str(z_min) + ' and ' + 'z = ' + str(z_max) + '.\n')
                file_object.close()

            #save average results in txt file
            avg_volume = round(np.mean(volume_drops),2)
            file_object = open(os.path.join(cur_dir,'results/' + str(dir) + '.txt'), 'a')
            file_object.write('\n' + 'The average V/V0 = ' + str(avg_volume))
            file_object.close()
            
            
