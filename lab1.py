from audioop import avg
import struct

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

BLACK = color(0,0,0)
WHITE = color(255,255,255)

class Render(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_color = WHITE
        self.clear()
        self.counter = 0

    def clear(self):
        self.framebuffer = [
            [WHITE for x in range(self.width)]
            for y in range(self.height)
        ]

    def draw(self, poligono):
        for i in range(len(poligono)):
            self.point(poligono[i][0],poligono[i][1])
            if i < len(poligono) - 1:
                self.line(poligono[i][0],poligono[i][1],poligono[i+1][0],poligono[i+1][1])
            else:
                self.line(poligono[i][0],poligono[i][1],poligono[0][0],poligono[0][1])
    def paintDraw(self, poligono):
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
                    self.line(xPoints[i],yPoints[i],xPoints[i+1],yPoints[i+1])
                    #divider
                    self.line(xPoints[i],yPoints[i],xPoints[i+1],yPoints[i+1]+1)
                    self.line(xPoints[i],yPoints[i],xPoints[i+1]+1,yPoints[i+1])
                    self.line(xPoints[i],yPoints[i],xPoints[i+1]-1,yPoints[i+1])
                    self.line(xPoints[i],yPoints[i],xPoints[i+1],yPoints[i+1]-1)
                    #divider
                    self.line(xPoints[i],yPoints[i]+1,xPoints[i+1],yPoints[i+1])
                    self.line(xPoints[i],yPoints[i]-1,xPoints[i+1],yPoints[i+1])
                    self.line(xPoints[i]+1,yPoints[i],xPoints[i+1],yPoints[i+1])
                    self.line(xPoints[i]-1,yPoints[i],xPoints[i+1],yPoints[i+1])
                    #divider
                    self.line(xPoints[i],yPoints[i]+1,xPoints[i+1],yPoints[i+1]+1)
                    self.line(xPoints[i],yPoints[i]-1,xPoints[i+1],yPoints[i+1]+1)
                    self.line(xPoints[i]+1,yPoints[i],xPoints[i+1],yPoints[i+1]+1)
                    self.line(xPoints[i]-1,yPoints[i],xPoints[i+1],yPoints[i+1]+1)
                    #divider
                    self.line(xPoints[i],yPoints[i]+1,xPoints[i+1],yPoints[i+1]-1)
                    self.line(xPoints[i],yPoints[i]-1,xPoints[i+1],yPoints[i+1]-1)
                    self.line(xPoints[i]+1,yPoints[i],xPoints[i+1],yPoints[i+1]-1)
                    self.line(xPoints[i]-1,yPoints[i],xPoints[i+1],yPoints[i+1]-1)
                    #divider
                    self.line(xPoints[i],yPoints[i]+1,xPoints[i+1]+1,yPoints[i+1])
                    self.line(xPoints[i],yPoints[i]-1,xPoints[i+1]+1,yPoints[i+1])
                    self.line(xPoints[i]+1,yPoints[i],xPoints[i+1]+1,yPoints[i+1])
                    self.line(xPoints[i]-1,yPoints[i],xPoints[i+1]+1,yPoints[i+1])
                    #divider
                    self.line(xPoints[i],yPoints[i]+1,xPoints[i+1]-1,yPoints[i+1])
                    self.line(xPoints[i],yPoints[i]-1,xPoints[i+1]-1,yPoints[i+1])
                    self.line(xPoints[i]+1,yPoints[i],xPoints[i+1]-1,yPoints[i+1])
                    self.line(xPoints[i]-1,yPoints[i],xPoints[i+1]-1,yPoints[i+1])

                else:
                    self.line(xPoints[i],yPoints[i],xPoints[0],yPoints[0])
                    self.line(xPoints[i],yPoints[i],xPoints[0],yPoints[0]+1)
                    self.line(xPoints[i],yPoints[i],xPoints[0]+1,yPoints[0])
                    self.line(xPoints[i],yPoints[i],xPoints[0]-1,yPoints[0])
                    self.line(xPoints[i],yPoints[i],xPoints[0],yPoints[0]-1)

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
        self.framebuffer[x][y] = self.current_color

    def set_current_color(self, c):
        self.current_color = c

    def line(self, x0,y0,x1,y1):
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
                self.point(y,x)
            else:
                self.point(x,y)

            offset += dy * 2
            if offset >= threshold:
                y +=1 if y0 < y1 else -1
                threshold += dx * 2

    def lineIntento(self,x1, y1, x2, y2):
        dy = y2 - y1
        dx = x2 - x1
        m = dy/dx

        steep = dy > dx

        if steep:
            x1,y1 = y1,x1
            x2,y2 = y2,x2
        y = y1
        for x in range(x1, x2+1):
            y = y1 + (-m if steep else m) * (x1 - x)
            self.point(x,round(y))
            

r = Render(900, 900)
r.set_current_color(BLACK)

#poligono 1
estrella = [(165, 380), (185, 360), (180, 330), (207, 345), (233, 330),
 (230, 360), (250, 380), (220, 385), (205, 410), (193, 383)]
r.set_current_color(color(255,208,0))
r.draw(estrella)
r.paintDraw(estrella)

#poligono 2
rombo = [(321, 335), (288, 286), (339, 251), (374, 302)]
r.set_current_color(color(0,255,4))
r.draw(rombo)
r.paintDraw(rombo)

#poligono 3
triangulo = [(377, 249), (411, 197), (436, 249)]
r.set_current_color(color(255,0,0))
r.draw(triangulo)
r.paintDraw(triangulo)

#poligono 4
poligono4 = [(413, 177), (448, 159), (502, 88), (553, 53), (535, 36), 
(676, 37),(660, 52),(750, 145), (761, 179), (672, 192), (659, 214), 
(615, 214), (632, 230), (580, 230),(597, 215), (552, 214), (517, 144), (466, 180)]
r.set_current_color(color(100,76,76))
r.draw(poligono4)
r.paintDraw(poligono4)

#poligono 5
poligono5 = [(682, 175), (708, 120), (735, 148), (739, 170)]
r.set_current_color(WHITE)
r.draw(poligono5)
r.paintDraw(poligono5)

r.write('a.bmp')