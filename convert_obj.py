class Obj(object):
    def __init__(self, filename):
        with open(filename) as f:
            self.lines = f.read().splitlines()
        
        self.vertices = []
        self.tvertices = []
        self.nvertices = []
        self.faces = []

        for lines in self.lines:
            if len(lines) >1:
                prefix, value = lines.split(' ', 1)
            #en caso que tenga un vacio al inicio eliminarlo
            if value[0] == ' ':
                value = value[1:]
            if prefix[0] == ' ':
                prefix = prefix[1:]

            if prefix == 'v':
                self.vertices.append(
                    list(
                        map(float, value.split(' '))
                        )
                    )

            if prefix == 'vt':
                self.tvertices.append(
                    list(
                        map(float, value.split(' '))
                        )
                    )

            if prefix == 'vn':
                self.nvertices.append(
                    list(
                        map(float, value.split(' '))
                        )
                    )

            if prefix == 'f':
                try:
                    self.faces.append([
                        list(map(int, face.split('/'))) 
                            for face in value.split(' ')
                        ]
                    )
                except:
                    self.faces.append([
                        list(map(int, face.split('//'))) 
                            for face in value.split(' ')
                        ]
                    )