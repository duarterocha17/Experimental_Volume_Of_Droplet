import os
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
import math

class Flood_Fill:  

    def reduce_size(self, im, factor_reduction = 1):
        # percent of original size
        width = int(im.shape[1] * factor_reduction)
        height = int(im.shape[0] *  factor_reduction)
        dim = (width, height)
        
        # resize image
        resized = cv.resize(im, dim, interpolation = cv.INTER_AREA)
        return(resized, factor_reduction)
    
    def neighbors(self, node, matrix):
        dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        result = []
        for dir in dirs:
            neighbor = [node[0] + dir[0], node[1] + dir[1]]
            if neighbor[0] < len(matrix) and neighbor[0] >= 0 and neighbor[1] < len(matrix[0]) and neighbor[1] >= 0:
                result.append(neighbor)
        return result

    def neighbors_dict(self, matrix):
        neighbors_dict = {}
        for column in range(len(matrix[0])):
            for row in range(len(matrix)):
                node = [row, column]
                neighbors_dict[str(node)] = self.neighbors(node, matrix)
        return(neighbors_dict)

    def is_fluid(self, matrix, node):
            if matrix[node[0],node[1]] == 255:
                return True
            else:
                return False

    def flood_fill(self, point, matrix, droplets_nodes_list, neighbors_dict, islands):

        row = point[0]
        col = point[1]

        q = []  # init empty queue (FIFO)
        matrix[row][col] = -1  # mark as visited
        q.append([row, col])  # add to queue
        droplets_points = [] # add points of droplet to list

        while len(q) > 0:
            cur_point = q[0]
            del q[0]
            for item in neighbors_dict[str(cur_point)]:
                if self.is_fluid(matrix, item):
                    droplets_points.append(item)
                    matrix[item[0],item[1]] = -1
                    q.append(item)
            droplets_nodes_list[islands] = (droplets_points)