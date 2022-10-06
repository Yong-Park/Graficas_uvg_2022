from array import array

class Matrix(object):
    # Matrix multiplication A @ B
    def __init__(self, matrix: array):
        self.matrix = matrix   

    def __matmul__(self, B):
        N = len(self.matrix)
        # print('self: ', self.matrix)
        M = len(self.matrix[0])
        # print('B: ', B.matrix)
        if type(B.matrix[0]) is list:
            P = len(B.matrix[0])
        else:
            P = 1
        
        result = []
        
        for i in range(N):
            result.append([])
            for j in range(P):
                result[i].append(0)
        # print('N ', N)
        # print('M ', M)
        # print('P ', P)
        if type(B.matrix[0]) is list:
            for i in range(N):
                for j in range(P):
                    for k in range(M):
                        result[i][j] += self.matrix[i][k] * B.matrix[k][j]
        else:
            # print('N ', N)
            # print('P ', P)
            # print('M ', M)
            for i in range(N):
                for j in range(P):
                    for k in range(M):
                        result[i][j] += self.matrix[i][k] * B.matrix[k]
        # print('result ', result)
        return Matrix(result)
