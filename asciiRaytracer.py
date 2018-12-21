#asciiRaytracer.py

import sys, tty, termios
import subprocess
import math, random
import threading
import time

#I want easier syntax for declaring arrays
def array(x,y,init=0):
    return [[init] * y for i in range(x)]

#vector of any size class
class vector:
    v = []
    def __init__ (self,v=[]):
        self.v = v
    def __add__ (self, other):
        result = vector([])
        if(len(self.v) == len(other.v)):
            for i in range(len(self.v)):
                result.v.append(self.v[i] + other.v[i])
        else:
            print("trying to add vectors of diff lengths")
        return result
    def __sub__ (self, other):
        result = vector([])
        if(len(self.v) == len(other.v)):
            for i in range(len(self.v)):
                result.v.append(self.v[i] - other.v[i])
        else:
            print("trying to sub vectors of diff lengths")
        return result
    def __mul__(self, other):
        result = vector([])
        for i in range(len(self.v)):
            result.v.append(self.v[i] * other)
        return result
    def __getitem__(self,key):
        return self.v[key]
    def __setitem__(self,key,item):
        self.v[key] = item
    def dot(self, other):
        result = vector([])
        if(len(self.v) == len(other.v)):
            for i in range(len(self.v)):
                result.v.append(self.v[i] * other.v[i])
        else:
            print("trying to get dot product of vectors of diff lengths")
        return result
    def magnitude(self):
        result = 0
        for term in self.v:
            result += term*term
        return result**0.5
    def normalized(self):
        mag = self.magnitude()
        if(mag == 0):
            return self
        return self * (1/mag)
    def toList(self):
        return self.v
    def toString(self):
        sys.stdout.write("( ")
        for i in range(len(self.v)):
            sys.stdout.write(str(self.v[i]))
            if(i < len(self.v)-1):
                sys.stdout.write(", ")
        sys.stdout.write(" )\n")

#ray class for raytracing
class Ray:
    origin = vector([0,0,0])
    direction = vector([0,0,1])
    zero = False
    def __init__(self,origin,direction,zero=False):
        self.origin = origin
        self.direction = direction.normalized()
        if(self.direction[0] == 0 and self.direction[1] == 0):
            self.zero = True

#line segment
class Edge:
    def __init__ (self,p1=vector([0,0]),p2=vector([0,1])):
        self.p1 = p1
        self.p2 = p2
    def intersect(self,ray):
        if(ray.zero):
            return None
        t = None
        r1 = ray.origin
        r2 = ray.direction + r1 #assumed to be normalized
        # x1,x2,x3,x4 = r1[0],r2[0],self.p1[0],self.p2[0]
        # y1,y2,y3,y4 = r1[1],r2[1],self.p1[1],self.p2[1]
        a = r1[0]-self.p1[0]
        b = self.p1[1]-self.p2[1]
        c = r1[1]-self.p1[1]
        d = self.p1[0]-self.p2[0]
        e = r1[0]-r2[0]
        f = r1[1]-r2[1]
        denom = e*b-f*d
        if(denom == 0):
            return None
        t = (a*b-c*d) / denom
        u = -(e*c-f*a) / denom
        if(t <= 0 or u < 0 or u > 1):
            return None
        return t

class Light: 
    def __init__ (self,pos = vector([0,0]),brightness=1):
        self.pos = pos

#static variable which controls whether the program is still running or not
gameOver = [False]

#ACSII display stuff
fps = 24 #this is the target frame rate
charsPerSec = 24 #this is how many characters getch() can take in per second, basically making it an input rate.
pixelAspectRatio = 2 #this is the ratio height / width for one character of text in whatever terminal you're using. Will make it adjust to different terminals later.
#might actually be 46/22
screenAspectRatio = 0.6 #this is the ratio height / width for the whole screen
screenWidth = 100
screenHeight = int((screenAspectRatio*screenWidth) / pixelAspectRatio)
print(screenWidth*screenHeight)
leftBound = int(-screenWidth / 2)
rightBound = int(screenWidth / 2)
topBound = int(screenHeight / 2)
bottomBound = int(-screenHeight / 2)
pixels = array(screenWidth,screenHeight,' ')
brightnessRamp = " `.',:~-_;\"!+/\\r|1<>v*?iLc()xJtfnYz{}Il]uj[CoaZXhkwUm%qOd$#bp8WM0&QB▒"#optimized for brightness order
largeDistance = 124
playerBrightness = 1

t = 0
dt = 1 / fps
objects = [
    Edge(vector([2,0]),vector([1.5,1.5])),
    Edge(vector([0,2]),vector([2,2])),
    Edge(vector([2,2]),vector([2,0])),
    Edge(vector([0,2]),vector([1.5,1.5])),
    # Edge(vector([-2,-1]),vector([2,-2])),
]

class Cam: #camera
    def __init__ (self,x=0,y=0,zoomConstant=1):
        self.x = x
        self.y = y
        self.zoomConstant = zoomConstant
    def zoomTo(self,newZoom):
        self.zoomConstant = newZoom
    def moveTo(self,x,y):
        self.x = x
        self.y = y
    def moveUp(self):
        self.y += 1.25 / self.zoomConstant
    def moveDown(self):
        self.y -= 1.25 / self.zoomConstant
    def moveLeft(self):
        self.x -= 1.25 / self.zoomConstant
    def moveRight(self):
        self.x += 1.25 / self.zoomConstant

class Player: #player
    def __init__ (self,x=0,y=0,speed=1):
        self.x = x
        self.y = y
        self.speed = speed
    def moveUp(self):
        global dt
        self.y += self.speed*dt
    def moveDown(self):
        global dt
        self.y -= self.speed*dt
    def moveLeft(self):
        global dt
        self.x -= self.speed*dt
    def moveRight(self):
        global dt
        self.x += self.speed*dt

camera = Cam(zoomConstant = 3)
player = Player(speed = 4.51)
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
tty.setraw(sys.stdin.fileno())

def clearScreen():
    subprocess.call(["tput", "reset"])

#self contained getch() if you need to use it for anything else
def getch():
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

#the critical step of getch()
def getch2():
    return sys.stdin.read(1)

def round(num):
    return int(num+0.5)
def abs(num):
    if(num<0):
        num = -num
    return num

def magnitude(x,y):
    return math.sqrt(x*x + y*y)
def magnitudeSqr(x,y):
    return x*x + y*y

def shadowrayHit(ray, normSquare=None):
    for obj in objects:
        t = obj.intersect(ray)
        if(t is not None):
            if(t*t < normSquare):
                return True
    return False

def getPositionForPixel(x,y,camx,camy,zoomConstant):
    spacex = camx + x / (zoomConstant * pixelAspectRatio)
    spacey = camy + y / zoomConstant
    return (spacex, spacey)

def brightness(x,y):
    # if(random.random()<0.5):
    #     return 0
    normSquare = magnitudeSqr(x-player.x,y-player.y)
    # global largeDistance
    # if(normSquare>largeDistance):
    #     return 0
    shadowray = Ray(vector([x,y]),vector([player.x-x,player.y-y]))
    if(shadowrayHit(shadowray,normSquare)):
        return 0
    global playerBrightness
    origbrightness = playerBrightness / (normSquare+1)
    salt = 0.03 * (1 - origbrightness)
    return origbrightness + random.uniform(-salt,0)

#a debug in case I ever need to test the brightness ramp again
def brightness2(x,y):
    global t
    return int(y) / 256

def brightnessToSymbol(val):
    if(val < 0):
        return brightnessRamp[0]
    elif(val > 1):
        return brightnessRamp[-1]
    else:
        return brightnessRamp[round(val*(len(brightnessRamp)-1))]

def getPixelForPosition(x,y,camx,camy,zoomConstant):
    dx = x - camx
    dy = y - camy
    spacex = dx * zoomConstant * pixelAspectRatio
    spacey = dy * zoomConstant
    pixelx = int(spacex)
    pixely = int(spacey)
    return (pixelx,pixely)

def isOnScreen(pixel):
    pixelx = pixel[0]
    pixely = pixel[1]
    if(pixelx < rightBound and pixelx >= leftBound):
        if(pixely < topBound and pixely >= bottomBound):
            return True
    return False
 
def printEverything(stuff):
    #retrace pixels
    for y in range(bottomBound, topBound):
        for x in range(leftBound, rightBound):
            pos = getPositionForPixel(x,y,camera.x,camera.y,camera.zoomConstant)
            pixels[x][y] = brightnessToSymbol(brightness(pos[0],pos[1]))

    #scoop pixels into frame buffer
    buf = ''
    for y in reversed(range(bottomBound, topBound)):
        for x in range(leftBound, rightBound):
            buf += pixels[x][y]
        buf += '\n\r'

    #clear and reprint buffer
    clearScreen()
    sys.stdout.write(buf)

def takePlayerInput():
    while not gameOver[0]:
        keycode = getch2()[0]
        if(keycode == 'x'):
            gameOver[0] = True
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        elif(keycode == 'i'):
            camera.moveUp()
        elif(keycode == 'j'):
            camera.moveLeft()
        elif(keycode == 'k'):
            camera.moveDown()
        elif(keycode == 'l'):
            camera.moveRight()
        elif(keycode == 'w'):
            player.moveUp()
        elif(keycode == 'a'):
            player.moveLeft()
        elif(keycode == 's'):
            player.moveDown()
        elif(keycode == 'd'):
            player.moveRight()
        elif(keycode == '-'):
            camera.zoomTo(0.95*camera.zoomConstant)
        elif(keycode == '='):
            camera.zoomTo(1.05*camera.zoomConstant)

def gameUpdate(stuff,t):
    stuff.clear()
    for i in range(50):
            stuff.append([i/10,math.sin(t*i/10)+i/10])

def render(stuff):
    gameOver[0] = False #so we can render if we ended previously
    global t, dt
    t = 0
    dt = 1/fps
    iteration = 0

    #main loop
    global playerBrightness
    global smallBrightness
    while not gameOver[0]:
        # gameUpdate(stuff,t)
        printEverything(stuff)
        # time.sleep(1/fps)
        t += dt
        iteration += 1
        #flickering light
        playerBrightness = 1 + random.uniform(-0.3,0.3)

stuff = []
inputThread = threading.Thread(target=takePlayerInput).start()
renderThread = threading.Thread(target=render(stuff))
renderThread.daemon = True
renderThread.start()

