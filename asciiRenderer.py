#asteroids.py

import sys, tty, termios
import subprocess
import math, random

#static variable which controls whether the program is still running or not
gameOver = [False]

#ACSII display stuff
fps = 12 #this is how many characters getch() can take in per second, basically making it a frame rate.
pixelAspectRatio = 2.0 #this is the ratio height / width for one character of text in whatever terminal you're using. Will make it adjust to different terminals later.
screenAspectRatio = 0.6 #this is the ratio height / width for the whole screen
screenWidth = 180
screenHeight = int((screenAspectRatio*screenWidth) / pixelAspectRatio)
leftBound = int(-screenWidth / 2)
rightBound = int(screenWidth / 2)
topBound = int(screenHeight / 2)
bottomBound = int(-screenHeight / 2)
pixels = {}
for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

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
        self.y += 2 / self.zoomConstant
    def moveDown(self):
        self.y -= 2 / self.zoomConstant
    def moveLeft(self):
        self.x -= 2 / self.zoomConstant
    def moveRight(self):
        self.x += 2 / self.zoomConstant

camera = Cam(zoomConstant = 20)

#display / input stuff
def clearScreen():
    subprocess.call(["clear"])

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


def printEverything(points):
    #clear pixels
    for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

    #refill pixels
    for p in points:
        pixel = getPixelForPosition(p[0],p[1],camera.x,camera.y,camera.zoomConstant)
        if(isOnScreen(pixel)):
            pixels[pixel] = '.'

    #print row by row
    for y in reversed(range(bottomBound, topBound)):
        thisRow = ''
        for x in range(leftBound, rightBound):
            thisRow += pixels[(x,y)]
        print(thisRow)

def printEverythingLayers(layers):
    #clear pixels
    for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

    #refill pixels
    for layer in layers:
        for p in layer:
            pixel = getPixelForPosition(p[0],p[1],camera.x,camera.y,camera.zoomConstant)
            if(isOnScreen(pixel)):
                pixels[pixel] = '.'

    #print row by row
    for y in reversed(range(bottomBound, topBound)):
        thisRow = ''
        for x in range(leftBound, rightBound):
            thisRow += pixels[(x,y)]
        print(thisRow)

def takePlayerInput():
    input = getch()[0]

    if(input == 'x'):
        gameOver[0] = True
    elif(input == 'w'):
        camera.moveUp()
    elif(input == 'a'):
        camera.moveLeft()
    elif(input == 's'):
        camera.moveDown()
    elif(input == 'd'):
        camera.moveRight()
    elif(input == '-'):
        camera.zoomTo(0.9*camera.zoomConstant)
    elif(input == '='):
        camera.zoomTo(1.1*camera.zoomConstant)

def render(stuff,layers=False):
    #main loop
    while not gameOver[0]:
        clearScreen()
        if(layers):
            printEverythingLayers(stuff)
        else:
            printEverything(stuff)
        takePlayerInput()

