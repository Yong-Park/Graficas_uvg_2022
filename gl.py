from re import A
from texture import *
from numpy import *
from vector import *
from convert_obj import *
from lib import *

class Render(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_color = BLACK
        self.clear()
        self.vertex_buffer_object = []
        self.active_vertex_array = []
        self.active_texture = None
        self.light = V3(0,0,-1)
        self.Model = None
        self.View = None

    def loadModelMatrix(self,translate =(0,0,0), scale=(1,1,1), rotate = (0,0,0)):
        translate = V3(*translate)
        scale = V3(*scale)
        rotate = V3(*rotate)

        translation_matrix = matrix([
            [1,0,0,translate.x],
            [0,1,0,translate.y],
            [0,0,1,translate.z],
            [0,0,0,1],
        ])

        scale_matrix = matrix([
            [scale.x,0,0,0],
            [0,scale.y,0,0],
            [0,0,scale.z,0],
            [0,0,0,1],
        ])
        
        a = rotate.x
        rotation_x = matrix([
            [1,0,0,0],
            [0,cos(a),-sin(a),0],
            [0,sin(a),cos(a),0],
            [0,0,0,1],
        ])
        a = rotate.y
        rotation_y = matrix([
            [cos(a),0,sin(a),0],
            [0,1,0,0],
            [-sin(a),0,cos(a),0],
            [0,0,0,1],
        ])
        a = rotate.z
        rotation_z = matrix([
            [cos(a),-sin(a),0,0],
            [sin(a),cos(a),0,0],
            [0,0,1,0],
            [0,0,0,1],
        ])

        rotation_matrix = rotation_x @ rotation_y @ rotation_z

        self.Model = translation_matrix @ rotation_matrix @ scale_matrix

    def write(self,filename):
        writebmp(filename,self.width,self.height,self.framebuffer)

    def lookAt(self, eye, center, up):
        z = (eye - center).norm()
        x = (up * z).norm()
        y = (z * x).norm()

        self.loadViewMatrix(x,y,z,center)

    def loadViewMatrix(self, x, y, z, center):
        Mi = matrix([
            [x.x,x.y,x.z,0],
            [y.x,y.y,y.z,0],
            [z.x,z.y,z.z,0],
            [0,0,0,1]
        ])

        O = matrix([
            [1,0,0,-center.x],
            [0,1,0,-center.y],
            [0,0,1,-center.z],
            [0,0,0,1]
        ])

        self.View = Mi @ O
        

    def clear(self):
        self.framebuffer = [
            [WHITE for x in range(self.width)]
            for y in range(self.height)
        ]
        self.zBuffer = [
            [-9999 for x in range(self.width)]
            for y in range(self.height)
        ]

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
        
        points = line_algorithm(x0,y0,x1,y1)
        for point in points:
            self.point(*point)

    def triangle_babycenter(self):
        A = next(self.active_vertex_array)
        B = next(self.active_vertex_array)
        C = next(self.active_vertex_array)

        if self.active_texture:
            tA = next(self.active_vertex_array)
            tB = next(self.active_vertex_array)
            tC = next(self.active_vertex_array)

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
                try:
                    if (self.zBuffer[x][y] < z):
                        self.zBuffer[x][y] = z

                        if self.active_texture:
                            tx = tA.x * w +tB.x * u + tC.x * v
                            ty = tA.y * w +tB.y * u + tC.y * v
                            self.current_color = self.active_texture.get_color_with_intensity(tx,ty,i)
                        self.point(y,x)
                except:
                    pass

    def triangle_wireframe(self):
        A = next(self.active_vertex_array)
        B = next(self.active_vertex_array)
        C = next(self.active_vertex_array)

        if self.active_texture:
            tA = next(self.active_vertex_array)
            tB = next(self.active_vertex_array)
            tC = next(self.active_vertex_array)
        
        self.line(A,B)
        self.line(B,C)
        self.line(C,A)
    
    #para darle un tamaño al dibujo
    def transform_vertex(self, vertex):
        augmented_vertex = [
            vertex[0],
            vertex[1],
            vertex[2],
            1
        ]

        transformed_vertex =  self.Model @ augmented_vertex @ self.View
        transformed_vertex = V3(transformed_vertex)
        
        return V3(
            transformed_vertex.x/transformed_vertex.w,
            transformed_vertex.y/transformed_vertex.w,
            transformed_vertex.z/transformed_vertex.w,
        )

    #esta convertira el .obj y lo renderizara
    def render_obj(self, objecto, translate=(0,0,0), scale=(1,1,1), rotate=(0,0,0)):
        self.loadModelMatrix(translate,scale,rotate)
        renderizar = Obj(objecto)
        #para que siempre este en el centro
        for face in renderizar.faces:
            if len(face) == 4:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1

                v1 = self.transform_vertex(renderizar.vertices[f1])
                v2 = self.transform_vertex(renderizar.vertices[f2])
                v3 = self.transform_vertex(renderizar.vertices[f3])
                v4 = self.transform_vertex(renderizar.vertices[f4])
                
                #Primera parte del triangulo
                self.vertex_buffer_object.append(v1)
                self.vertex_buffer_object.append(v2)
                self.vertex_buffer_object.append(v3)
                
                if self.active_texture:

                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1
                    ft4 = face[3][1] - 1

                    vt1 = V3(*renderizar.tvertices[ft1])
                    vt2 = V3(*renderizar.tvertices[ft2])
                    vt3 = V3(*renderizar.tvertices[ft3])
                    vt4 = V3(*renderizar.tvertices[ft4])

                    self.vertex_buffer_object.append(vt1)
                    self.vertex_buffer_object.append(vt2)
                    self.vertex_buffer_object.append(vt3)
                #segunda parte del triangulo
                self.vertex_buffer_object.append(v1)
                self.vertex_buffer_object.append(v3)
                self.vertex_buffer_object.append(v4)

                if self.active_texture:

                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1
                    ft4 = face[3][1] - 1

                    vt1 = V3(*renderizar.tvertices[ft1])
                    vt2 = V3(*renderizar.tvertices[ft2])
                    vt3 = V3(*renderizar.tvertices[ft3])
                    vt4 = V3(*renderizar.tvertices[ft4])

                    self.vertex_buffer_object.append(vt1)
                    self.vertex_buffer_object.append(vt3)
                    self.vertex_buffer_object.append(vt4)

            if len(face) == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = self.transform_vertex(renderizar.vertices[f1])
                v2 = self.transform_vertex(renderizar.vertices[f2])
                v3 = self.transform_vertex(renderizar.vertices[f3])
                
                self.vertex_buffer_object.append(v1)
                self.vertex_buffer_object.append(v2)
                self.vertex_buffer_object.append(v3)

                if self.active_texture:

                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1

                    vt1 = V3(*renderizar.tvertices[ft1])
                    vt2 = V3(*renderizar.tvertices[ft2])
                    vt3 = V3(*renderizar.tvertices[ft3])

                    self.vertex_buffer_object.append(vt1)
                    self.vertex_buffer_object.append(vt2)
                    self.vertex_buffer_object.append(vt3)

        self.active_vertex_array = iter(self.vertex_buffer_object)

    def draw(self,polygon):
        if polygon == 'TRIANGLES':
            try:
                while True:
                    self.triangle_babycenter()
            except StopIteration:
                print("terminado")
        if polygon == 'WIREFRAME':
            try:
                while True:
                    self.triangle_wireframe()
            except StopIteration:
                print("terminado")

pi =3.1416
                        
scale_factor = (400,400,500)
translate_factor = (512,512, 0)
rotate_factor = (0,pi/3,0)
r = Render(1024, 1024)
r.set_current_color(BLACK)
r.lookAt(V3(-5,0,10),V3(0,0,0),V3(0,1,0))
r.active_texture = Texture("./modelos/Penguin.bmp")
r.render_obj('./modelos/Penguin.obj',translate_factor,scale_factor,rotate_factor)
r.draw('TRIANGLES') 
r.write('t.bmp')