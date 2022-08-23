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
  
    #inicialice cualquier objeto interno que requiera su software renderer
    def __init__(self):
        self.width = 0
        self.height = 0
        self.portWidth= 0
        self.portHeight= 0
        self.portX=0
        self.portY=0
        self.texture = None
        self.current_color = WHITE
        
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
        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[x][y])

        f.close()

    def point(self, x, y):
        if (0 < x < self.width and 0 < y < self.height):
            self.framebuffer[x][y] = self.current_color

    def set_current_color(self, c):
        self.current_color = c

    #inicialice su framebuffer con un tamaño (la imagen resultante va a ser de este tamaño
    def glCreateWindow(self, width, lenght):
        if width >=0 and lenght >=0:
          self.width = width
          self.height = lenght
        else: 
          self.width = abs(width)
          self.height = abs(lenght)
        
        self.framebuffer = [
            [BLACK for x in range(self.width)]
            for y in range(self.height)
        ]
        self.zBuffer = [
            [-9999 for x in range(self.width)]
            for y in range(self.height)
        ]


    #defina el área de la imagen sobre la que se va a poder dibujar
    def glViewPort(self,x,y,width,height):
      if x >= 0 and y >= 0 and width >=0 and height >=0:
        self.portWidth = width
        self.portHeight = height
        self.portX=x
        self.portY=y
      else:
        self.portWidth = abs(width)
        self.portHeight = abs(height)
        self.portX= abs(x)
        self.portY= abs(y)

    #llene el mapa de bits con un solo color
    def glClear(self):
      for x in range(self.portX, self.portX+self.portWidth+1):
        for y in range(self.portY, self.portY+self.portHeight+1):
          self.point(y,x)
      self.set_current_color(BLACK)
    
    #se pueda cambiar el color con el que funciona glClear(). Los parámetros deben ser números en el rango de 0 a 1.
    def glClearColor(self,r,g,b):
      if (0<=r<=1) and (0<=g<=1) and (0<=b<=1):
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
      else:
        r=g=b = 0
      self.set_current_color(color(r,g,b))
      for x in range(self.portX, self.portX+self.portWidth+1):
        for y in range(self.portY, self.portY+self.portHeight+1):
          self.point(y,x)
      self.set_current_color(BLACK)
    
    #pueda cambiar el color de un punto de la pantalla. Las coordenadas x, y son relativas al viewport que definieron con glViewPort.
    def glVertex(self,x,y):
      #revisar si no supera el el 1 o -1
      if -1 <= x <= 1:
        if -1 <= y <= 1:
          pass
        else:
          y = 0
      else:
        x = 0
      self.pixel_X = int((x+1) * self.portWidth * 1/2 ) + self.portX
      self.pixel_Y = int((y+1) * self.portHeight * 1/2) + self.portY
      self.point(self.pixel_Y,self.pixel_X)
    
    #se pueda cambiar el color con el que funciona glVertex(). Los parámetros deben ser números en el rango de 0 a 1.
    def glColor(self,r,g,b):
      if (0<=r<=1) and (0<=g<=1) and (0<=b<=1):
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
      else:
        r=g=b = 0
      self.set_current_color(color(r,g,b))

    #glLine para dibujar lineas
    def glLine(self, x0,y0,x1,y1):
      #revisar si estan en el rango de -1 a 1
      if not(-1 <= x0 <= 1): 
        x0 = 0
      if not(-1 <= y0 <= 1):
        y0 = 0
      if not(-1 <= x1 <= 1):
        x1 = 0
      if not(-1 <= y1 <= 1):
        y1 = 0

      #convertir los valores
      x0 = int((x0+1) * self.portWidth * 1/2 ) + self.portX
      y0 = int((y0+1) * self.portHeight * 1/2) + self.portY

      x1 = int((x1+1) * self.portWidth * 1/2 ) + self.portX
      y1 = int((y1+1) * self.portHeight * 1/2) + self.portY

      #realizar conversion
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
      dx = abs(x1-x0)

      offset = 0
      threshold = dx
      y = y0

      for x in range(x0,x1+1):
        if steep:
            self.point(x,y)
        else:
            self.point(y,x)

        offset += dy * 2
        if offset >= threshold:
          y += 1 if y0 < y1 else -1
          threshold += dx * 2
    
    #para dibujar un poligono con sus puntos x,y
    def glDraw(self, poligono):
        for i in range(len(poligono)):
            self.point(round(poligono[i][0]),round(poligono[i][1]))
            if i < len(poligono) - 1:
                self.line((poligono[i][0],poligono[i][1]),(poligono[i+1][0],poligono[i+1][1]))
            else:
                self.line((poligono[i][0],poligono[i][1]),(poligono[0][0],poligono[0][1]))
    
    #para pintar o rellenar el poligono
    def glPaintDraw(self, poligono):
        xPoints = []
        yPoints = []
        avgx = 0
        avgy = 0
        #guardar los puntos
        for i in range(len(poligono)):
            xPoints.append(poligono[i][0])
            yPoints.append(poligono[i][1])
        #obtener el promedio de los puntos de x
        for i in xPoints:
            avgx += i
        avgx = int(avgx / len(xPoints))
        #obtener el promedio d elos puntos de y
        for i in yPoints:
            avgy += i
        avgy = int(avgy / len(yPoints))
        
        dist = int(( (xPoints[0] - avgx)**2 + (yPoints[0] - avgy)**2 )**(1/2))
        
        for i in range(dist + 1):
            for j in range(len(xPoints)):
                #revisar en x
                if xPoints[j] < avgx:
                    xPoints[j] += 1
                elif xPoints[j] == avgx:
                    pass
                else:
                    xPoints[j] -= 1
                #revisar en y
                if yPoints[j] < avgy:
                    yPoints[j] += 1
                elif yPoints[j] == avgy:
                    pass 
                else:
                    yPoints[j] -= 1
            for i in range(len(poligono)):
                if i < len(poligono) -1:
                    self.line((xPoints[i],yPoints[i]),(xPoints[i+1],yPoints[i+1]))
                    #divider
                    self.line((xPoints[i],yPoints[i]),(xPoints[i+1],yPoints[i+1]+1))
                    self.line((xPoints[i],yPoints[i]),(xPoints[i+1]+1,yPoints[i+1]))
                    self.line((xPoints[i],yPoints[i]),(xPoints[i+1]-1,yPoints[i+1]))
                    self.line((xPoints[i],yPoints[i]),(xPoints[i+1],yPoints[i+1]-1))
                    #divider
                    self.line((xPoints[i],yPoints[i]+1),(xPoints[i+1],yPoints[i+1]))
                    self.line((xPoints[i],yPoints[i]-1),(xPoints[i+1],yPoints[i+1]))
                    self.line((xPoints[i]+1,yPoints[i]),(xPoints[i+1],yPoints[i+1]))
                    self.line((xPoints[i]-1,yPoints[i]),(xPoints[i+1],yPoints[i+1]))
                    #divider
                    self.line((xPoints[i],yPoints[i]+1),(xPoints[i+1],yPoints[i+1]+1))
                    self.line((xPoints[i],yPoints[i]-1),(xPoints[i+1],yPoints[i+1]+1))
                    self.line((xPoints[i]+1,yPoints[i]),(xPoints[i+1],yPoints[i+1]+1))
                    self.line((xPoints[i]-1,yPoints[i]),(xPoints[i+1],yPoints[i+1]+1))
                    #divider
                    self.line((xPoints[i],yPoints[i]+1),(xPoints[i+1],yPoints[i+1]-1))
                    self.line((xPoints[i],yPoints[i]-1),(xPoints[i+1],yPoints[i+1]-1))
                    self.line((xPoints[i]+1,yPoints[i]),(xPoints[i+1],yPoints[i+1]-1))
                    self.line((xPoints[i]-1,yPoints[i]),(xPoints[i+1],yPoints[i+1]-1))
                    #divider
                    self.line((xPoints[i],yPoints[i]+1),(xPoints[i+1]+1,yPoints[i+1]))
                    self.line((xPoints[i],yPoints[i]-1),(xPoints[i+1]+1,yPoints[i+1]))
                    self.line((xPoints[i]+1,yPoints[i]),(xPoints[i+1]+1,yPoints[i+1]))
                    self.line((xPoints[i]-1,yPoints[i]),(xPoints[i+1]+1,yPoints[i+1]))
                    #divider
                    self.line((xPoints[i],yPoints[i]+1),(xPoints[i+1]-1,yPoints[i+1]))
                    self.line((xPoints[i],yPoints[i]-1),(xPoints[i+1]-1,yPoints[i+1]))
                    self.line((xPoints[i]+1,yPoints[i]),(xPoints[i+1]-1,yPoints[i+1]))
                    self.line((xPoints[i]-1,yPoints[i]),(xPoints[i+1]-1,yPoints[i+1]))

                else:
                    self.line((xPoints[i],yPoints[i]),(xPoints[0],yPoints[0]))
                    self.line((xPoints[i],yPoints[i]),(xPoints[0],yPoints[0]+1))
                    self.line((xPoints[i],yPoints[i]),(xPoints[0]+1,yPoints[0]))
                    self.line((xPoints[i],yPoints[i]),(xPoints[0]-1,yPoints[0]))
                    self.line((xPoints[i],yPoints[i]),(xPoints[0],yPoints[0]-1))

    def render_obj(self, objecto, scale=(1,1,1), translate=(0,0,0)):
      renderizar = Obj(objecto)
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

    def line(self, p1,p2):
        x0 = round(p1[0])
        y0 = round(p1[1])
        x1 = round(p2[0])
        y1 = round(p2[1])
        
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

    #posicion de la luz
    def lightPosition(self,x:int,y:int,z:int):
        self.light = V3(x,y,z)
    #con zbuffer
    def triangle_babycenter(self, vertices, tvertices=()):
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
        for x in range(min.x, max.x + 1):
            for y in range(min.y, max.y + 1):
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
    
    #escriba el archivo de imagen
    def glFinish(self):
        self.write('a.bmp')

#pruebas
r = Render()
scale_factor = (6,6,16)
translate_factor = (512,512,0)
r.glCreateWindow(1024,1024)

r.lightPosition(2,-3,-1)
# r.texture = Texture('./modelos/model.bmp')
r.render_obj('./modelos/frost.obj',scale_factor,translate_factor)
r.glFinish()
