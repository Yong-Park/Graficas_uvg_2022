class Matrix(list):
    # Matrix multiplication A @ B

    def round(self):
        self.x = round(self.x)
        self.y = round(self.y)
        self.z = round(self.z)

    def __matmul__(self, B):
        
        N = len(self)
        print('self: ', self)
        M = len(self[0])
        print('B: ', B)
        if type(B[0]) is list:
            P = len(B[0])
        else:
            P = 1
        
        result = []
        for i in range(N):
            row = [0] * P
            result.append(row)
        if type(B[0]) is list:
            for i in range(N):
                for j in range(P):
                    for k in range(M):
                        result[i][j] += self[i][k] * B[k][j]
        else:
            for i in range(N):
                for j in range(P):
                    for k in range(M):
                        result[i][j] += self[i][k] * B[j]

        return result