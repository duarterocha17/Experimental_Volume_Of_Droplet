import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math

class Final_Analysis:

    def we(self, fluid, flow_rate, dict_properties, external_diameter=0.001, internal_diameter = 0.001, conv_to_si = 10**9):

        velocity = flow_rate/conv_to_si/(math.pi*internal_diameter**2*0.25)
        prop = dict_properties[fluid]
        we = prop['rho']*velocity**2*external_diameter/prop['sur_tension']

        return we

    def plot_droplets_volume(self, df, fluid, dict_external_diameters, dict_shapes, dict_properties):
        
        df = df.loc[df['fluid'] == fluid]
        fig, ax = plt.subplots()
        for nozzle in np.unique(df['nozzle'].values):
            df_aux = df.loc[df['nozzle'] == nozzle]
            flow_rate = df_aux['flow_rate'].values
            we = self.we(fluid, flow_rate, dict_properties) #,external_diameter=dict_external_diameters[nozzle]
            volume = df_aux['volume'].values
            ax.scatter(we, volume, marker=dict_shapes[nozzle])
            z = np.polyfit(we, volume, 1)
            p = np.poly1d(z)
            plt.plot(we,p(we))


        #add labels
        ax.set_ylabel('$V/V_0$', fontname="Helvetica", fontsize=15)
        ax.set_xlabel('$We$', fontname="Helvetica", fontsize=15)
        ax.grid(visible = True)
        ax.set_title('Results for ' + fluid)

        plt.show()

final = Final_Analysis()
external_diameters = {'Circ': 0.0012, 'Quad': 0.0014, 'Tri': 0.00176, 'Curv': 0.00276}
shapes = {'Circ': "o", 'Quad': "s", 'Tri': "^", 'Curv': "2"}
properties_fluid = {
    'glycerol':{
        'rho': 1260,
        'sur_tension': 0.0634,
        'viscosity': 1.412},
    'water':{
        'rho': 1000,
        'sur_tension': 0.0728,
        'viscosity': 0.001
    }
    }
df = pd.read_csv('/Volumes/Duarte/Master Thesis/Experiments/Experimental_Volume_Of_Droplet/data/results/final_droplet_df.csv')
final.plot_droplets_volume(df, 'glycerol', external_diameters, shapes, properties_fluid)