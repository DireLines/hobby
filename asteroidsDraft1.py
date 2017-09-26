#asteroids.py

import sys, tty, termios
import subprocess
import math, random

gameOver = [False]

#setting up ACSII display stuff
pixelAspectRatio = 2.0 #this is the ratio height / width for one character of text in whatever terminal you're using. Will make it adjust to different terminals later.
screenAspectRatio = 0.6 #this is the ratio height / width for the whole screen
screenWidth = 250
screenHeight = int((screenAspectRatio*screenWidth) / pixelAspectRatio)
leftBound = int(-screenWidth / 2)
rightBound = int(screenWidth / 2)
topBound = int(screenHeight / 2)
bottomBound = int(-screenHeight / 2)
pixels = {}
for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

historyFrame = [1]
jumps = [[]]

class Asteroid: #object within the game
    def __init__ (self,x=0,y=0,vel_x=0,vel_y=0,accel_x=0,accel_y=0):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.accel_x = accel_x
        self.accel_y = accel_y
    def stepForward(self, dt=1):
        # x = x_0 + v_0*t + 1/2*a*t^2
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        self.x += self.accel_x * 0.5 * dt**2
        self.y += self.accel_y * 0.5 * dt**2

        #v = v_0 + a*t
        self.vel_x += self.accel_x * dt
        self.vel_y += self.accel_y * dt

class History: #positions of stuff over time
    def __init__ (self, data=[], steps=2000, frame=0):
        self.data = data
        self.steps = steps
        self.frame = frame
    def fill(self, board, dt=0.01):
        data = []
        for i in range(self.steps):
            data.append([])
            for ast in board:
                ast.stepForward(dt)
                data[i].append((ast.x,ast.y))
        self.data = data
    def frameForward(self, numFrames=1):
        if(numFrames+self.frame < len(self.data)):
            self.frame += numFrames
    def frameBackward(self, numFrames=1):
        if(self.frame-numFrames >= 0):
            self.frame -= numFrames
    def stuffAtFrame(self):
        return self.data[self.frame]


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

def seedBoard(board):
    numAsteroids = 200
    for i in range(numAsteroids):
        board.append(Asteroid(x=random.randrange(-30,30),y=random.randrange(-30,30),vel_x = random.randrange(-5,5), vel_y = random.randrange(-5,5)))
    return board

camera = Cam()
board = []
history = History()

seedBoard(board)
history.fill(board)


def dist(p1,p2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    dx = x2 - x1
    dy = y2 - y1

    return math.sqrt(dx*dx + dy*dy)

def midpoint(p1,p2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    dxover2 = (x2 - x1) / 2
    dyover2 = (y2 - y1) / 2

    return((x1 + dxover2, y1 + dyover2))

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

# def isVisible(pixel, sightRange):
#     if(dist(pixel,[player.x,player.y]) <= sightRange):
#         return True
#     return False

def fillInPossibleJumps(asteroids, hopDistance):
    jumpPositions = []
    for i in range(len(asteroids)):
        asteroid = asteroids[i]
        for j in range(i+1,len(asteroids)):
            otherAst = asteroids[j]
            if(dist(asteroid,otherAst) <= hopDistance):
                mid = midpoint(asteroid,otherAst)
                quarter = midpoint(asteroid,mid)
                threequarters = midpoint(otherAst,mid)
                jumpPositions.append(mid)
                jumpPositions.append(quarter)
                jumpPositions.append(threequarters)
                jumpPositions.append(midpoint(asteroid,quarter))
                jumpPositions.append(midpoint(quarter,mid))
                jumpPositions.append(midpoint(mid,threequarters))
                jumpPositions.append(midpoint(threequarters,otherAst))
    return jumpPositions

def fillInJumpsFromPos(pos, asteroids, hopDistance):
    jumpPositions = []
    for asteroid in asteroids:
        if(asteroid != pos and dist(pos, asteroid) <= hopDistance):
            mid = midpoint(asteroid,pos)
            quarter = midpoint(asteroid,mid)
            threequarters = midpoint(pos,mid)
            jumpPositions.append(mid)
            jumpPositions.append(quarter)
            jumpPositions.append(threequarters)
            jumpPositions.append(midpoint(asteroid,quarter))
            jumpPositions.append(midpoint(quarter,mid))
            jumpPositions.append(midpoint(mid,threequarters))
            jumpPositions.append(midpoint(threequarters,pos))
    return jumpPositions

def printEverything():
    #clear pixels
    for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

    #refill pixels
    asteroids = history.stuffAtFrame()
    if(historyFrame[0] != history.frame):
        historyFrame[0] = history.frame
        jumps[0] = fillInPossibleJumps(asteroids,4)
    # if(historyFrame[0] != history.frame):
    #     historyFrame[0] = history.frame
    #     jumps[0] = fillInJumpsFromPos(asteroids[0],asteroids,4)
    for j in jumps[0]:
        pixel = getPixelForPosition(j[0],j[1],camera.x,camera.y,camera.zoomConstant)
        if(isOnScreen(pixel)):
            pixels[pixel] = '.'
    for asteroid in asteroids:
        pixel = getPixelForPosition(asteroid[0],asteroid[1],camera.x,camera.y,camera.zoomConstant)
        if(isOnScreen(pixel)):
            pixels[pixel] = 'o'


    #print row by row
    for y in reversed(range(bottomBound, topBound)):
        thisRow = ''
        for x in range(leftBound, rightBound):
            thisRow = thisRow + pixels[(x,y)]
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
    elif(input == '.'):
        history.frameForward()
    elif(input == ','):
        history.frameBackward()
    elif(input == '/'):
        history.frameForward(6)
    elif(input == 'm'):
        history.frameBackward(6)
    elif(input == '0'):
        history.frame = 0



while not gameOver[0]:
    clearScreen()
    printEverything()
    takePlayerInput()
