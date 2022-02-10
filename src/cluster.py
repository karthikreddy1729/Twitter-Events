"""
DBSCAN code
"""

import numpy as np
import scipy as sc
import json
import scipy.spatial as sp
from scipy.spatial.kdtree import distance_matrix
from sklearn import cluster
# from CreateEmbeddings import CreateEmbeddings

class DBSCAN:

    def __init__(self, tweets, segments, eps = 0.8, minPts = 30):
        self.tweets = tweets
        self.segments = segments
        self.C = 0
        self.clusters = []
        self.clusterList = []
        self.eps = eps
        self.minPts = minPts
        self.pointClusterNumberIndex = 1
        

    def create_sparse_mat(self):
        self.sparse_matrix = []
        for tweet in self.tweets:
            mat_2d = np.zeros(shape=(len(tweet), len(self.segments) + 1))
            for i, word in enumerate(tweet):
                for context_id in self.segments[word].embeddings:
                    context_idx=self.segments[context_id].index
                    mat_2d[i][context_idx]+=1
            self.sparse_matrix.append(np.sum(mat_2d, axis=0))  
        row_sums = np.sum(self.sparse_matrix, axis=1)
        # self.sparse_matrix = np.array(self.sparse_matrix)
        self.sparse_matrix = self.sparse_matrix/row_sums[:, np.newaxis] 
    
    def cosineSimMatrix(self):
        print(self.sparse_matrix.shape)
        return sp.distance.squareform(sp.distance.pdist(self.sparse_matrix, 'cosine'))

    def getNeighbours(self, dist_matrix, p_idx):
        return np.where(dist_matrix[p_idx]>self.eps)[0]

    def cluster(self):
        self.create_sparse_mat()
        distanceMatrix = self.cosineSimMatrix()
        self.type = np.zeros(shape=(len(self.sparse_matrix)))
        self.pointToCluster = np.zeros(shape=(len(self.sparse_matrix)))
        visited = np.zeros(shape=(len(self.sparse_matrix)))
        for idx, dataPoint in enumerate(self.sparse_matrix): 
            if visited[idx] == 0:
                visited[idx] = 1
                pointNeighbours = self.getNeighbours(distanceMatrix, idx)
                if len(pointNeighbours) < self.minPts:
                    self.type[idx] = -1
                else:
                    for k in range(len(self.clusters)):
                        self.clusters.pop()
                    self.clusters.append(idx)
                    self.pointToCluster[idx] = self.pointClusterNumberIndex

                    self.expandCluster(self.tweets[idx], pointNeighbours, visited, distanceMatrix)
                    self.clusters.append(pointNeighbours[:])
                    self.clusterList.append(self.clusters[:])
                    self.pointClusterNumberIndex = self.pointClusterNumberIndex+1

    def expandCluster(self, P, PNeighbours, visited, distanceMatrix, ):
        neighbours = []
        for i in PNeighbours:
            if visited[i] == 0:
                visited[i] = 1
                neighbours = self.getNeighbours(distanceMatrix, i)
                if len(neighbours) >= self.minPts:
                    for j in neighbours:
                        try:
                            PNeighbours[j]
                        except:
                            np.append(PNeighbours, j)
            if self.pointToCluster[i] == 0:
                self.clusters.append(i)
                self.pointToCluster[i]=self.pointClusterNumberIndex

    def stats(self):
        op_dict = {}
        clusterAllocations = np.array(self.pointToCluster, 'int')
        for idx, cls in enumerate(clusterAllocations):
            if str(cls) not in op_dict.keys():
                op_dict[str(cls)] = []
            op_dict[str(cls)].append(self.tweets[idx])
        # print(op_dict)
        with open('output.json', 'w') as f:
            json.dump(op_dict, f)

