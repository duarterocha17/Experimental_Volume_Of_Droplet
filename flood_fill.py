import cv2 as cv

class Flood_Fill:  

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
            droplets_nodes_list[islands] = (droplets_points) 