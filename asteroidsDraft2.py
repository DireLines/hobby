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
jumpDistance = [4]

class Asteroid: #object within the game
    def __init__ (self,x=0,y=0,vel_x=0,vel_y=0,accel_x=0,accel_y=0, symbol='o'):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.accel_x = accel_x
        self.accel_y = accel_y
        self.symbol = symbol
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
    def __init__ (self, data=[], steps=3000, frame=0):
        self.data = data
        self.steps = steps
        self.frame = frame
    def fill(self, board, dt=0.01):
        data = []
        for i in range(self.steps):
            data.append([])
            for ast in board:
                ast.stepForward(dt)
                data[i].append((ast.x,ast.y,ast.symbol))
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

def getPerpendicularVector(p1,p2,magnitude):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    originalLength = dist(p1,p2)
    return (-dy * magnitude / originalLength, dx * magnitude / originalLength)

def getDirectionVector(p1,p2,magnitude):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    originalLength = dist(p1,p2)
    return(dx * magnitude / originalLength, dy * magnitude / originalLength)





def seedBoard(board):
    baseVelocity = 0.5
    #Rock at the center
    board.append(Asteroid(symbol='R'))
    #80 asteroids in inner solar system
    numAsteroids = 0
    maxAsteroids = 80
    solarSystemRadius = 20
    while(numAsteroids < maxAsteroids):
        posx = random.uniform(-solarSystemRadius,solarSystemRadius)
        posy = random.uniform(-solarSystemRadius,solarSystemRadius)
        if(dist((posx,posy),(0,0)) <= solarSystemRadius):
            numAsteroids += 1
            tangentToCenter = getPerpendicularVector((posx,posy),(0,0),3*baseVelocity)
            board.append(Asteroid(x=posx,y=posy,vel_x = tangentToCenter[0] + random.uniform(-2.3*baseVelocity,2.3*baseVelocity), vel_y = tangentToCenter[1] + random.uniform(-2.3*baseVelocity,2.3*baseVelocity)))
    #90 asteroids scattered through inner and outer solar system
    numAsteroids = 0
    maxAsteroids = 90
    solarSystemRadius = 40
    while(numAsteroids < maxAsteroids):
        posx = random.uniform(-solarSystemRadius,solarSystemRadius)
        posy = random.uniform(-solarSystemRadius,solarSystemRadius)
        if(dist((posx,posy),(0,0)) <= solarSystemRadius):
            numAsteroids += 1
            tangentToCenter = getPerpendicularVector((posx,posy),(0,0),5*baseVelocity)
            board.append(Asteroid(x=posx,y=posy,vel_x = tangentToCenter[0] + random.uniform(-3.5*baseVelocity,3.5*baseVelocity), vel_y = tangentToCenter[1] + random.uniform(-3.5*baseVelocity,3.5*baseVelocity)))
    #2 small clouds of comets
    numAsteroids = 0
    maxAsteroids = 20
    offsetX = 70
    offsetY = 0
    target = (0,-8)
    regionRadius = 10
    while(numAsteroids < maxAsteroids):
        posx = random.uniform(-regionRadius,regionRadius)
        posy = random.uniform(-regionRadius,regionRadius)
        if(dist((posx,posy),(0,0)) <= regionRadius):
            numAsteroids  += 1
            posx += offsetX
            posy += offsetY
            toCenter = getDirectionVector((posx,posy),target,10*baseVelocity)
            board.append(Asteroid(x=posx,y=posy,vel_x = toCenter[0] + random.uniform(-1*baseVelocity,1*baseVelocity), vel_y = toCenter[1] + random.uniform(-1*baseVelocity,1*baseVelocity)))
    numAsteroids = 0
    maxAsteroids = 10
    offsetX = -40
    offsetY = 85
    target = (2.5,6)
    regionRadius = 10
    while(numAsteroids < maxAsteroids):
        posx = random.uniform(-regionRadius,regionRadius)
        posy = random.uniform(-regionRadius,regionRadius)
        if(dist((posx,posy),(0,0)) <= regionRadius):
            numAsteroids  += 1
            posx += offsetX
            posy += offsetY
            toCenter = getDirectionVector((posx,posy),target,12*baseVelocity)
            board.append(Asteroid(x=posx,y=posy,vel_x = toCenter[0] + random.uniform(-1*baseVelocity,1*baseVelocity), vel_y = toCenter[1] + random.uniform(-1*baseVelocity,1*baseVelocity)))
    return board


camera = Cam()
board = []
history = History()

seedBoard(board)
history.fill(board)


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

def fillInPossibleJumps(asteroids):
    jumpPositions = []
    for i in range(len(asteroids)):
        asteroid = asteroids[i]
        for j in range(i+1,len(asteroids)):
            otherAst = asteroids[j]
            if(dist(asteroid,otherAst) <= jumpDistance[0]):
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

def printEverything():
    #clear pixels
    for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

    #refill pixels
    asteroids = history.stuffAtFrame()
    if(historyFrame[0] != history.frame):
        historyFrame[0] = history.frame
        jumps[0] = fillInPossibleJumps(asteroids)
    # if(historyFrame[0] != history.frame):
    #     historyFrame[0] = history.frame
    #     jumps[0] = fillInJumpsFromPos(asteroids[0],asteroids)
    for j in jumps[0]:
        pixel = getPixelForPosition(j[0],j[1],camera.x,camera.y,camera.zoomConstant)
        if(isOnScreen(pixel)):
            pixels[pixel] = '.'
    for asteroid in asteroids:
        pixel = getPixelForPosition(asteroid[0],asteroid[1],camera.x,camera.y,camera.zoomConstant)
        if(isOnScreen(pixel)):
            pixels[pixel] = asteroid[2]

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
    elif(input == 'k'):
        jumpDistance[0] -= 0.5
    elif(input == 'l'):
        jumpDistance[0] += 0.5



while not gameOver[0]:
    clearScreen()
    printEverything()
    takePlayerInput()
