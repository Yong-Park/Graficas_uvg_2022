from texture import *
from vector import *
from convert_obj import *
from lib import *
from matrix import *
from math import *

class Render(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_color = BLACK
        self.clear()
        self.vertex_buffer_object = []
        self.active_vertex_array = []
        self.active_texture = None
        self.active_shader = None
        self.light = V3(0,0,1)
        self.Model = None
        self.View = None

    def loadModelMatrix(self,translate =(0,0,0), scale=(1,1,1), rotate = (0,0,0)):
        translate = V3(*translate)
        scale = V3(*scale)
        rotate = V3(*rotate)

        translation_matrix = Matrix([
            [1,0,0,translate.x],
            [0,1,0,translate.y],
            [0,0,1,translate.z],
            [0,0,0,1],
        ])

        scale_matrix = Matrix([
            [scale.x,0,0,0],
            [0,scale.y,0,0],
            [0,0,scale.z,0],
            [0,0,0,1],
        ])
        
        a = rotate.x
        rotation_x = Matrix([
            [1,0,0,0],
            [0,cos(a),-sin(a),0],
            [0,sin(a),cos(a),0],
            [0,0,0,1],
        ])
        a = rotate.y
        rotation_y = Matrix([
            [cos(a),0,sin(a),0],
            [0,1,0,0],
            [-sin(a),0,cos(a),0],
            [0,0,0,1],
        ])
        a = rotate.z
        rotation_z = Matrix([
            [cos(a),-sin(a),0,0],
            [sin(a),cos(a),0,0],
            [0,0,1,0],
            [0,0,0,1],
        ])
        # print("___")
        # print('x rotation: ', rotation_x)
        # print('y rotation: ', rotation_y)
        # print('z rotation: ', rotation_z)
        rotation_matrix = rotation_x @ rotation_y @ rotation_z
        # print("___")
        # print('transtaltion_matrix: ',translation_matrix)
        # print('rotation_matrix: ',rotation_matrix)
        # print('scale_matrix: ',scale_matrix)
        self.Model = translation_matrix @ rotation_matrix @ scale_matrix
        # print('self model: ', self.Model)

    def write(self,filename):
        writebmp(filename,self.width,self.height,self.framebuffer)

    def lookAt(self, eye, center, up):
        z = (eye - center).norm()
        x = (up * z).norm()
        y = (z * x).norm()

        self.loadViewMatrix(x,y,z,center)
        self.loadProjectionMatrix(eye,center)
        self.loadViewportMatrix()

    def loadViewMatrix(self, x, y, z, center):
        Mi = Matrix([
            [x.x,x.y,x.z,0],
            [y.x,y.y,y.z,0],
            [z.x,z.y,z.z,0],
            [0,0,0,1]
        ])

        Op = Matrix([
            [1,0,0,-center.x],
            [0,1,0,-center.y],
            [0,0,1,-center.z],
            [0,0,0,1]
        ])
        # print(Mi.matrix)
        # print(Op.matrix)

        self.View = Mi @ Op
        
        
    def loadProjectionMatrix(self,eye,center):
        coeff = -1/(eye.__length__() - center.__length__())
        self.Projection = Matrix([
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,coeff,1],
        ])

    def loadViewportMatrix(self):
        x= 0
        y= 0
        w = self.width/2
        h = self.height/2

        self.Viewport = Matrix([
            [w,0,0,x+w],
            [0,h,0,y+h],
            [0,0,128,128],
            [0,0,0,1],
        ])


    def clear(self):
        self.framebuffer = [
            [BLACK for x in range(self.width)]
            for y in range(self.height)
        ]
        self.zBuffer = [
            [-9999 for x in range(self.width)]
            for y in range(self.height)
        ]
        
    def shader(self, **kwargs):
        w,u,v = kwargs['bar']
        Light = kwargs['light']
        A,B,C = kwargs['vertices']
        tA, tB, tC = kwargs['texture_coordinates']
        nA, nB, nC = kwargs['normals']
        
        iA = nA.norm() @ Light.norm()    
        iB = nB.norm() @ Light.norm()   
        iC = nC.norm() @ Light.norm()

        i = iA * w + iB * u + iC * v   
        # print('i: ', i) 

        if self.active_texture:
            tx = tA.x * w +tB.x * u + tC.x * v
            ty = tA.y * w +tB.y * u + tC.y * v
            # print('tx ', tx)
            # print('ty ', ty)

            return self.active_texture.get_color_with_intensity(tx,ty,i)

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
        # print('A: ', A)
        B = next(self.active_vertex_array)
        # print('B: ', B)
        C = next(self.active_vertex_array)
        # print('C: ', C)

        if self.active_texture:
            tA = next(self.active_vertex_array)
            tB = next(self.active_vertex_array)
            tC = next(self.active_vertex_array)
            # print('tA: ', tA)
            # print('tB: ', tB)
            # print('tC: ', tC)
        if self.active_shader:
            nA = next(self.active_vertex_array)
            nB = next(self.active_vertex_array)
            nC = next(self.active_vertex_array)
            # print('nA: ', nA)
            # print('nB: ', nB)
            # print('nC: ', nC)

        min,max = bounding_box(A,B,C)
        min.round()
        max.round()
        # print('____')
        # print('min: ', min)
        # print('max: ', max)
        # print('min x: ', min.x)
        # print('min y: ', min.y)
        # print('max x: ', max.x)
        # print('max y: ', max.y)
        for x in range(min.x, max.x+1):
            for y in range(min.y, max.y+1):
                w, v, u = barycentric(A,B,C, V3(x,y))

                if (w < 0 or v < 0 or u < 0):
                    continue

                z = A.z * w + B.z * v + C.z * u
                if (x >= 0 and
                    y >= 0 and
                    x < len(self.zBuffer) and  
                    y < len(self.zBuffer[0]) and 
                    self.zBuffer[x][y] < z):
                    self.zBuffer[x][y] = z
                    self.current_color = self.active_shader(
                        bar = (w,u,v),
                        vertices=(A,B,C),
                        texture_coordinates = (tA,tB,tC),
                        normals = (nA,nB,nC),
                        light = self.light,
                        coorinates = (x,y)
                        )
                    # print('puntos')
                    # print(self.current_color)
                    # print(y,x)
                    # print()
                    self.point(y,x)

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
    
    #para darle un tama??o al dibujo
    def transform_vertex(self, vertex):
        augmented_vertex = Matrix([
            vertex[0],
            vertex[1],
            vertex[2],
            1
        ])
        # print()
        # print(self.Viewport.matrix)
        # print(self.Projection.matrix)
        # print(self.View.matrix)
        # print(self.Model.matrix)
        # print(augmented_vertex.matrix)
        transformed_vertex =  self.Viewport @ self.Projection @ self.View @ self.Model @ augmented_vertex 
        # print('transformed_vertex: ', transformed_vertex.matrix)
        transformed_vertex = V3(transformed_vertex)
        # print(transformed_vertex.x/transformed_vertex.w,
        #     transformed_vertex.y/transformed_vertex.w,
        #     transformed_vertex.z/transformed_vertex.w,)
        # x = transformed_vertex.x/transformed_vertex.w
        # y = transformed_vertex.y/transformed_vertex.w
        # z = transformed_vertex.z/transformed_vertex.w

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
        # print('+++++')
        # print('transformando los vertices')
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

                    vt1 = V3(*renderizar.tvertices[ft1])
                    vt2 = V3(*renderizar.tvertices[ft2])
                    vt3 = V3(*renderizar.tvertices[ft3])

                    self.vertex_buffer_object.append(vt1)
                    self.vertex_buffer_object.append(vt2)
                    self.vertex_buffer_object.append(vt3)

                try:
                    fn1 = face[0][2] - 1
                    fn2 = face[1][2] - 1
                    fn3 = face[2][2] - 1

                    vn1 = V3(*renderizar.nvertices[fn1])
                    vn2 = V3(*renderizar.nvertices[fn2])
                    vn3 = V3(*renderizar.nvertices[fn3])
                
                    self.vertex_buffer_object.append(vn1)
                    self.vertex_buffer_object.append(vn2)
                    self.vertex_buffer_object.append(vn3)
                except:
                    pass
                #segunda parte del triangulo
                self.vertex_buffer_object.append(v1)
                self.vertex_buffer_object.append(v3)
                self.vertex_buffer_object.append(v4)

                if self.active_texture:

                    ft1 = face[0][1] - 1
                    ft3 = face[2][1] - 1
                    ft4 = face[3][1] - 1

                    vt1 = V3(*renderizar.tvertices[ft1])
                    vt3 = V3(*renderizar.tvertices[ft3])
                    vt4 = V3(*renderizar.tvertices[ft4])

                    self.vertex_buffer_object.append(vt1)
                    self.vertex_buffer_object.append(vt3)
                    self.vertex_buffer_object.append(vt4)
                try:
                    fn1 = face[0][2] - 1
                    fn3 = face[2][2] - 1
                    fn4 = face[3][2] - 1

                    vn1 = V3(*renderizar.nvertices[fn1])
                    vn3 = V3(*renderizar.nvertices[fn3])
                    vn4 = V3(*renderizar.nvertices[fn4])
                
                    self.vertex_buffer_object.append(vn1)
                    self.vertex_buffer_object.append(vn3)
                    self.vertex_buffer_object.append(vn4)
                except:
                    pass

            if len(face) == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = self.transform_vertex(renderizar.vertices[f1])
                # print('v1 ', v1)
                v2 = self.transform_vertex(renderizar.vertices[f2])
                # print('v2 ', v2)
                v3 = self.transform_vertex(renderizar.vertices[f3])
                # print('v3 ', v3)
                # print()

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
                
                try:
                    fn1 = face[0][2] - 1
                    fn2 = face[1][2] - 1
                    fn3 = face[2][2] - 1

                    vn1 = V3(*renderizar.nvertices[fn1])
                    vn2 = V3(*renderizar.nvertices[fn2])
                    vn3 = V3(*renderizar.nvertices[fn3])
                
                    self.vertex_buffer_object.append(vn1)
                    self.vertex_buffer_object.append(vn2)
                    self.vertex_buffer_object.append(vn3)
                except:
                    pass

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
import random

def marte(**kwargs):
    x,y = kwargs['coorinates']
    #arriba
    if y > 760 - random.randint(0,50) and x > 500 - random.randint(0,50) and x < 550 + random.randint(0,50):
        return color(109,104,96)
    elif x < 500 + random.randint(0,50):
        if x > 300- random.randint(0,50) and x < 450 + random.randint(0,50):
            if 450 - random.randint(0,50) < y < 450 + random.randint(0,50):
                return color(128,112,80)
            elif 400 - random.randint(0,50) < x < 450 + random.randint(0,50):
                if 400 - random.randint(0,50) < y < 450 + random.randint(0,50):
                    return color(128,112,80)
            if x > 350 - random.randint(0,50):
                if 600 - random.randint(0,50) < y < 650 + random.randint(0,50):
                    return color(128,112,80)
        return color(168,101,75)
    elif y < 250 + random.randint(0,50) and x > 500 - random.randint(0,50) and x < 550 + random.randint(0,50):
        return color(109,104,96)
        
    elif x >= 400:
        i = (x - 400)*0.4
        r = 168 - i 
        g = 101 - i
        b = 75 - i
        
        if 500 - random.randint(0,50) < x < 600 + random.randint(0,50):
            if 400 - random.randint(0,50)< y < 550 + random.randint(0,50):
                return color(98,78,68)
        if 680 - random.randint(0,50) < x < 700 + random.randint(0,50):
            if 400 - random.randint(0,50)< y < 650 + random.randint(0,50):
                return color(58,38,28)
        if 0<=r<=255:
            pass
        else:
            r = 0
        if 0<=g<=255:
            pass
        else:
            g = 0
        if 0<=b<=255:
            pass
        else:
            b = 0
        return color(r,g,b)

def phobos(**kwargs):
    x,y = kwargs['coorinates']
    if 820 - random.randint(0,5)< x < 830 + random.randint(0,5):
        if 500 - random.randint(0,5)< y < 510 + random.randint(0,5):
            return color(188,188,190)
    if x >= 750:
        i = (x - 750)*0.5
        r = 181 - i 
        g = 149 - i
        b = 128 - i
    if 0<=r<=255:
        pass
    else:
        r = 0
    if 0<=g<=255:
        pass
    else:
        g = 0
    if 0<=b<=255:
        pass
    else:
        b = 0
    return color(r,g,b)    
    
def deimos(**kwargs):
    x,y = kwargs['coorinates']
    if 970 - random.randint(0,5)< x < 980 + random.randint(0,5):
        if 510 - random.randint(0,5)< y < 520 + random.randint(0,5):
            return color(188,188,190)
    if x >= 850:
        i = (x - 750)*0.5
        r = 181 - i 
        g = 149 - i
        b = 128 - i
    if 0<=r<=255:
        pass
    else:
        r = 0
    if 0<=g<=255:
        pass
    else:
        g = 0
    if 0<=b<=255:
        pass
    else:
        b = 0
    return color(r,g,b)    

pi =3.1416
                        

r = Render(1024, 1024)
r.set_current_color(BLACK)
r.lookAt(V3(-1,0,5),V3(0,0,0),V3(0,1,0))
r.active_texture = Texture("./modelos/Flatland.bmp")
#pintar el fondo de pantalla
r.framebuffer = r.active_texture.pixels
r.active_shader = r.shader

#cubo de tierra
scale_factor = (1/20,1/20,1/20)
translate_factor = (-0.52,-0.25,1)
rotate_factor = (0,0,0)
r.active_texture = Texture("./modelos/Grass.bmp")
r.active_shader = r.shader
r.render_obj('./modelos/GRASS_BLOCK.obj',translate_factor,scale_factor,rotate_factor)
r.draw('TRIANGLES') 
#creeper
scale_factor = (1/6,1/6,1/6)
translate_factor = (2/3,0,0)
rotate_factor = (0,-pi/4,0)
r.active_texture = Texture("./modelos/creeper.bmp")
r.active_shader = r.shader
r.render_obj('./modelos/Creeper.obj',translate_factor,scale_factor,rotate_factor)
r.draw('TRIANGLES') 
#steve
scale_factor = (1/50,1/50,1/50)
translate_factor = (-2/4,-1/2,0)
rotate_factor = (0,-pi/6,0)
r.active_texture = Texture("./modelos/steve.bmp")
r.active_shader = r.shader
r.render_obj('./modelos/steve.obj',translate_factor,scale_factor,rotate_factor)
r.draw('TRIANGLES') 
#axe in head
scale_factor = (1/300,1/300,1/300)
translate_factor = (0.75,0.15,-0.1)
rotate_factor = (0,0,pi/4)
r.active_texture = Texture("./modelos/axe.bmp")
r.active_shader = r.shader
r.render_obj('./modelos/axe.obj',translate_factor,scale_factor,rotate_factor)
r.draw('TRIANGLES') 
#axe on ground
scale_factor = (1/200,1/200,1/200)
translate_factor = (0,-0.5,0)
rotate_factor = (-pi/3,0,0)
r.active_texture = Texture("./modelos/axe.bmp")
r.active_shader = r.shader
r.render_obj('./modelos/axe.obj',translate_factor,scale_factor,rotate_factor)
r.draw('TRIANGLES')
#bee
scale_factor = (1/100,1/100,1/100)
translate_factor = (0,-0.25,0)
rotate_factor = (0,-pi/8,0)
r.active_texture = Texture("./modelos/tnt.bmp")
r.active_shader = r.shader
r.render_obj('./modelos/tnt.obj',translate_factor,scale_factor,rotate_factor)
r.draw('TRIANGLES')

r.write('proyeto_1.bmp')

# r.draw('TRIANGLES') 
#para marte
# r.active_shader = marte
# r.render_obj('./modelos/sphere.obj',translate_factor,scale_factor,rotate_factor)
# r.draw('TRIANGLES') 
# #su luna phobos
# scale_factor = (1/8,1/8,1/8)
# translate_factor = (5/8,0,0)
# rotate_factor = (0,0,0)
# r.active_shader = phobos
# r.render_obj('./modelos/sphere.obj',translate_factor,scale_factor,rotate_factor)
# r.draw('TRIANGLES') 
# #luna deimos
# scale_factor = (1/8,1/8,1/8)
# translate_factor = (7/8,0,0)
# rotate_factor = (0,0,0)
# r.active_shader = deimos
# r.render_obj('./modelos/sphere.obj',translate_factor,scale_factor,rotate_factor)