import cv2 as cv
import numpy as np

class Flood_Fill:  
    
    def neighbors(self, node, matrix):
        
        '''
        Function to return neighbors of a node
        '''

        neighs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        result = []


        for neigh in neighs:
            neighbor = [node[0] + neigh[0], node[1] + neigh[1]]
            if neighbor[0] < len(matrix) and neighbor[0] >= 0 and neighbor[1] < len(matrix[0]) and neighbor[1] >= 0:
                result.append(neighbor)

        return result

    def neighbors_dict(self, matrix):

        '''
        Create a dictionary with each node as a key and neighbors as values.
        This way it is not necessary to loop through the neighbors every time
        the flood fill algorithm is called.
        '''

        neighbors_dict = {}

        for column in range(len(matrix[0])):
            for row in range(len(matrix)):
                node = [row, column]
                neighbors_dict[str(node)] = self.neighbors(node, matrix)
        return(neighbors_dict)

    def is_fluid(self, matrix, node):
        
        '''
        Evaluate if the node is in fluid or not.
        '''

        if matrix[node[0],node[1]] == 255:
            return True
        else:
            return False

    def flood_fill(self, point, matrix, droplets_nodes_list, neighbors_dict, islands):

        '''
        Flood fill algorithm
        '''

        row = point[0]
        col = point[1]

        q = []  # init empty queue (FIFO)
        matrix[row][col] = -1  # mark as visited
        q.append([row, col])  # add to queue
        droplets_points = [] # add nodes of droplet to list

        while len(q) > 0:
            cur_point = q[0]
            del q[0]
            for item in neighbors_dict[str(cur_point)]:
                if self.is_fluid(matrix, item):
                    droplets_points.append(item)
                    matrix[item[0],item[1]] = -1
                    q.append(item)

            #list of nodes of each droplet added to a dictionary, with key = islands        
            droplets_nodes_list[islands] = droplets_points

    def droplets_domain_dict(self, matrix, neighbors):
        
        '''
        Method to isolate the nodes of each droplet.
        '''

        islands = 0
        all_droplets = {}
        m = np.copy(np.array(matrix, np.int32))
        filtered_matrix = np.where(m == 255)

        #run flood fill for each droplet
        while len(filtered_matrix[0])>0:
            point = (filtered_matrix[0][0], filtered_matrix[1][0])
            if self.is_fluid(m,point):
                self.flood_fill(point, m, all_droplets, neighbors, islands)  
                islands += 1
            filtered_matrix = np.where(m == 255)
        
        return(islands, all_droplets)  

    def remove_satellites(self, all_droplets, islands, diameter_inlet, conv_px_m ,factor_reduction):
        
        '''
        Remove satellite droplets from dictionary of droplets
        '''

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