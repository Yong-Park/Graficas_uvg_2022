import struct
from texture import *
from vector import *
from random import randint
from convert_obj import *
def char(c):
    # 1 byte
    return struct.pack('=c',c.encode('ascii'))

def word(w):
    # 2  bytes
    return struct.pack('=h',w)

def dword(d):
    #4 bytes
    return struct.pack('=l', d)

def color (r,g,b):
    return bytes([b,g,r])

def cross(v1,v2):
    return (
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x
    )

def bounding_box(A,B,C):
    coors = [(A.x,A.y),(B.x,B.y),(C.x,C.y)]

    xmin = 999999
    xmax = -999999
    ymin = 999999
    ymax = -999999

    for (x,y) in coors:
        if x < xmin:
            xmin = x
        if x > xmax:
            xmax = x
        if y < ymin:
            ymin = y
        if y > ymax:
            ymax = y
    return V3(xmin, ymin), V3(xmax, ymax)

def barycentric(A,B,C,P):
    
    cx,cy,cz = cross(
        V3(B.x-A.x, C.x - A.x, A.x - P.x),
        V3(B.y-A.y, C.y - A.y, A.y - P.y)
    )
    if cz == 0:
        return(-1,-1,-1)
    u = cx / cz
    v = cy / cz
    w = 1 - (u + v) 

    return (w,v,u)


BLACK = color(0,0,0)
WHITE = color(255,255,255)

class Render(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_color = WHITE
        self.texture = None
        self.clear()

    def clear(self):
        self.framebuffer = [
            [WHITE for x in range(self.width)]
            for y in range(self.height)
        ]
        self.zBuffer = [
            [-9999 for x in range(self.width)]
            for y in range(self.height)
        ]

    def write(self, filename):
        f = open(filename, 'bw')

        #pixel header
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(word(0))
        f.write(word(0))
        f.write(dword(14 + 40))

        #info header
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        #pixel data
        for y in range(self.height):
            for x in range(self.width):
                f.write(self.framebuffer[y][x])

        f.close()

    def point(self, x, y):
        if (0 < x < self.width and 0 < y < self.height):
            self.framebuffer[x][y] = self.current_color

    def set_current_color(self, c):
        self.current_color = c

    def line(self, p1,p2):
        x0 = round(p1.x)
        y0 = round(p1.y)
        x1 = round(p2.x)
        y1 = round(p2.y)
        
        dy = abs(y1-y0)
        dx = abs(x1-x0)

        steep = dy > dx

        if steep:
            x0,y0 = y0,x0
            x1,y1 = y1,x1

        if  x0>x1:
            x0,x1 = x1,x0
            y0,y1 = y1,y0

        dy = abs(y1-y0)
        dx = x1-x0

        offset = 0
        threshold = dx
        y = y0

        for x in range(x0,x1 +1):
            if steep:
                self.point(x,y)
            else:
                self.point(y,x)
            offset += dy * 2
            if offset >= threshold:
                y +=1 if y0 < y1 else -1
                threshold += dx * 2
                
    def triangle(self, A,B,C):

        A.round()
        B.round()
        C.round()

        if A.y> B.y:
            A,B = B,A
        if A.y> C.y:
            A,C = C,A
        if B.y> C.y:
            B,C = C,B

        self.current_color = color(
            randint(0,255),
            randint(0,255),
            randint(0,255)
        )

        dx_ac = C.x -A.x
        dy_ac = C.y - A.y

        if dy_ac == 0:
            return
        
        m_ac = dx_ac / dy_ac

        dx_ab = B.x - A.x
        dy_ab = B.y - A.y

        if dy_ab != 0:
            m_ab = dx_ab/dy_ab
            for y in range(round(A.y), round(B.y) + 1):
                xi = round(A.x - m_ac * (A.y - y))
                xf = round(A.x - m_ab * (A.y - y))

                if xi > xf:
                    xi,xf= xf,xi

                for x in range(xi,xf + 1):
                    self.point(y,x)

        
        dx_bc = C.x - B.x
        dy_bc = C.y - B.y

        if dy_bc != 0:
            m_bc = dx_bc/dy_bc
            for y in range(round(B.y), round(C.y) + 1):
                xi = round(A.x - m_ac * (A.y - y))
                xf = round(B.x - m_bc * (B.y - y))

                if xi > xf:
                    xi,xf= xf,xi

                for x in range(xi,xf + 1):
                    self.point(y,x)

    #posicion de la luz
    def lightPosition(self,x:int,y:int,z:int):
        self.light = V3(x,y,z)

    def triangle_babycenter(self,vertices, tvertices=()):
        A,B,C = vertices
        if self.texture:
            tA,tB,tC = tvertices
        

        Light = self.light
        Normal = (B-A) * (C-A)
        i = Normal.norm() @ Light.norm()
        if i < 0:
            return

        self.current_color = color(
            round(255 * i),
            round(255 * i),
            round(255 * i)
        )

        min,max = bounding_box(A,B,C)
        min.round()
        max.round()
        for x in range(min.x, max.x+1):
            for y in range(min.y, max.y+1):
                w, v, u = barycentric(A,B,C, V3(x,y))

                if (w < 0 or v < 0 or u < 0):
                    continue

                z = A.z * w + B.z * v + C.z * u
                if (self.zBuffer[x][y] < z):
                    self.zBuffer[x][y] = z

                    if self.texture:
                        tx = tA.x * w +tB.x * u + tC.x * v
                        ty = tA.y * w +tB.y * u + tC.y * v

                        self.current_color = self.texture.get_color_with_intensity(tx,ty,i)
                    
                    self.point(y,x)
    
    #para darle un tamaño al dibujo
    def transform_vertex(self, vertex, scale, translate):
        return V3(
            (vertex[0] * scale[0]) + translate[0],
            (vertex[1] * scale[1]) + translate[1],
            (vertex[2] * scale[2]) + translate[2],
        )

    #esta convertira el .obj y lo renderizara
    def render_obj(self, objecto, scale=(1,1,1), translate=(0,0,0)):
        renderizar = Obj(objecto)
        #para que siempre este en el centro
        for face in renderizar.faces:
            if len(face) == 4:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1

                v1 = self.transform_vertex(renderizar.vertices[f1], scale, translate)
                v2 = self.transform_vertex(renderizar.vertices[f2], scale, translate)
                v3 = self.transform_vertex(renderizar.vertices[f3], scale, translate)
                v4 = self.transform_vertex(renderizar.vertices[f4], scale, translate)

                if self.texture:

                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1
                    ft4 = face[3][1] - 1

                    vt1 = V3(*renderizar.tvertices[ft1])
                    vt2 = V3(*renderizar.tvertices[ft2])
                    vt3 = V3(*renderizar.tvertices[ft3])
                    vt4 = V3(*renderizar.tvertices[ft4])

                    self.triangle_babycenter((v1,v2,v3), (vt1,vt2,vt3))
                    self.triangle_babycenter((v1,v3,v4), (vt1,vt3,vt4))
                else:
                    self.triangle_babycenter((v1,v2,v3))
                    self.triangle_babycenter((v1,v3,v4))
            if len(face) == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = self.transform_vertex(renderizar.vertices[f1], scale, translate)
                v2 = self.transform_vertex(renderizar.vertices[f2], scale, translate)
                v3 = self.transform_vertex(renderizar.vertices[f3], scale, translate)
                if self.texture:

                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1

                    vt1 = V3(*renderizar.tvertices[ft1])
                    vt2 = V3(*renderizar.tvertices[ft2])
                    vt3 = V3(*renderizar.tvertices[ft3])

                    self.triangle_babycenter((v1,v2,v3), (vt1,vt2,vt3))
                else:
                    self.triangle_babycenter((v1,v2,v3))

                        
scale_factor = (400,400,500)
translate_factor = (512,512, 0)
r = Render(1024, 1024)
r.lightPosition(0,0,-1)
r.set_current_color(WHITE)
r.texture = Texture("./modelos/Penguin.bmp")
r.render_obj('./modelos/Penguin.obj',scale_factor,translate_factor)
r.write('t.bmp')