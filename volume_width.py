import os
import matplotlib.pyplot as plt
import numpy as np
import math
from flood_fill import Flood_Fill
from file_handling import File_Handling

class Volume_Width:

    def call_flood_fill(self):
        #call class Flood_Fill
        self.ff = Flood_Fill()
    
    def call_file_handling(self):
        #call class File_Handling
        self.fh = File_Handling()

    def representation(self, nozzle_dir, im, x, y, name_subdir):

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
        fig.savefig(os.path.join(nozzle_dir, os.path.join('results', name_subdir[:name_subdir.rfind('.')] + '.png')),bbox_inches='tight', dpi=150)
        plt.close('all')


    def volume(self, im, conv_px_m, diameter_inlet = 0.001, factor_reduction = 1):

        '''
        Calculate volume of first non-satellite detached droplet for a droplet analysis.
        '''

        #import Flood_Fill class
        self.call_flood_fill()

        #get domain of first detached droplet
        neighbors = self.ff.neighbors_dict(im)
        islands, all_droplets = self.ff.droplets_domain_dict(im, neighbors)
        islands, all_droplets = self.ff.remove_satellites(all_droplets, islands, diameter_inlet, conv_px_m ,factor_reduction)
        
        #if there is more than one droplet, calculate volume for second island 
        if len(all_droplets.keys()) > 1:
            first_detached_droplet = np.array(all_droplets[list(all_droplets.keys())[1]])
        
        #else calculate for first island
        else:
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

        #get x domain of the droplet
        x_min = round(np.min(first_detached_droplet[:,1])*conv_px_m/factor_reduction/diameter_inlet,2)
        x_max = round(np.max(first_detached_droplet[:,1])*conv_px_m/factor_reduction/diameter_inlet,2)
        y_max = round(np.max(first_detached_droplet[:,0])*conv_px_m/factor_reduction/diameter_inlet,2)

        return(islands, volume_single_droplet, x_min, x_max, y_max)  

    def jet_width(self, im, conv_px_m, diameter_inlet = 0.001, factor_reduction = 1):
        '''
        Calculate jet's width for jet analysis
        '''
        
        #import Flood_Fill class
        self.call_flood_fill()

        #get jet width for initial length
        im_0_10_px = im[:,0:10]
        fluid_im_0_10_px = np.argwhere(im_0_10_px == 255)
        init_jet_width = round((np.max(fluid_im_0_10_px[:,0])-np.min(fluid_im_0_10_px[:,0]))*conv_px_m/factor_reduction/diameter_inlet,3)

        #get jet width after 1D of length
        d_to_px = round(2*diameter_inlet/conv_px_m)
        im_0_1d = im[:,d_to_px-5:d_to_px+5]
        fluid_im_0_1d = np.argwhere(im_0_1d == 255)
        jet_width_1d = round((np.max(fluid_im_0_1d[:,0])-np.min(fluid_im_0_1d[:,0]))*conv_px_m/factor_reduction/diameter_inlet,3)

        return(init_jet_width, jet_width_1d)
   

    
            
