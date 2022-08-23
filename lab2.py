from code import Render

r = Render()
r.glCreateWindow(600,400)
r.glViewPort(150,200,50,80) #x,y,width,height
r.glClear()
#r.glClearColor(131, 122, 82)
r.glColor(255,0,0)
r.glVertex(0,0)
r.glColor(255,0,255)
r.glVertex(0,1)
r.glFinish()