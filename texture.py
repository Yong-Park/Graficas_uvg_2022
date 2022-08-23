import struct

def color (r,g,b):
    return bytes([b,g,r])

class Texture:
    def __init__(self,path):
        self.path = path
        self.read()

    def read(self):
        with open(self.path, "rb") as image:
            image.seek(2 + 4 + 2 + 2)
            header_size = struct.unpack("=l",image.read(4))[0]
            image.seek(2 + 4 + 2 + 2 + 4 + 4)
            self.width = struct.unpack("=l",image.read(4))[0]
            self.height = struct.unpack("=l",image.read(4))[0]

            image.seek(header_size)

            self.pixels = []
            for y in range(self.height):
                self.pixels.append([])
                for x in range(self.width):
                    b = ord(image.read(1))
                    g = ord(image.read(1))
                    r = ord(image.read(1))
                    self.pixels[y].append(
                        color(r,g,b)
                    )

    def get_color(self,tx,ty):
        x = round(tx * self.width)
        y = round(ty * self.height)

        return self.pixels[y][x]

    def get_color_with_intensity(self,tx,ty,intensity):
        x = round(tx * self.width)
        y = round(ty * self.height)
        try:
            b = round(self.pixels[y][x][0] * intensity)
        except:
            b = 255 * intensity
        try:
            g = round(self.pixels[y][x][1] * intensity) 
        except:
            g = 255 * intensity
        try:
            r = round(self.pixels[y][x][2] * intensity)
        except:
            r = 255 * intensity
        return color(r,g,b)

# r = Render(1024,1024)
# t = Texture("./modelos/model.bmp")

# r.framebuffer = t.pixels
# renderizar = Obj("./modelos/model.obj")

# r.current_color = color(255,255,255)

# for face in renderizar.faces:
#     if len(face) == 3:
#         f1 = face[0][1] - 1
#         f2 = face[1][1] - 1
#         f3 = face[2][1] - 1

#         vt1 = V3(
#             renderizar.tvertices[f1][0] * t.width,
#             renderizar.tvertices[f1][1] * t.height,
#         )
#         vt2 = V3(
#             renderizar.tvertices[f2][0] * t.width,
#             renderizar.tvertices[f2][1] * t.height,
#         )
#         vt3 = V3(
#             renderizar.tvertices[f3][0] * t.width,
#             renderizar.tvertices[f3][1] * t.height,
#         )

#         r.line(vt1,vt2)
#         r.line(vt2,vt3)
#         r.line(vt3,vt1)

#     if len(face) == 4:
#         f1 = face[0][1] - 1
#         f2 = face[1][1] - 1
#         f3 = face[2][1] - 1
#         f4 = face[3][1] - 1

#         vt1 = V3(
#             renderizar.tvertices[f1][0] * t.width,
#             renderizar.tvertices[f1][1] * t.height,
#         )
#         vt2 = V3(
#             renderizar.tvertices[f2][0] * t.width,
#             renderizar.tvertices[f2][1] * t.height,
#         )
#         vt3 = V3(
#             renderizar.tvertices[f3][0] * t.width,
#             renderizar.tvertices[f3][1] * t.height,
#         )
#         vt4 = V3(
#             renderizar.tvertices[f4][0] * t.width,
#             renderizar.tvertices[f4][1] * t.height,
#         )

#         r.line(vt1,vt2)
#         r.line(vt2,vt3)
#         r.line(vt3,vt4)
#         r.line(vt4,vt1)

# r.write("t.bmp")