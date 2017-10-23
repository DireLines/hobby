#asteroids.py

import sys, tty, termios
import subprocess
import math, random

#static variable which controls whether the program is still running or not
gameOver = [False]

#ACSII display stuff
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


#some static variables
historyFrame = [1]
jumpDistance = [4]

#math helper functions
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


#class definitions
class Asteroid: #object within the game
    def __init__ (self,x=0,y=0,vel_x=0,vel_y=0,accel_x=0,accel_y=0, mass=1, symbol='o',properties=[]):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.accel_x = accel_x
        self.accel_y = accel_y
        self.mass = mass
        self.symbol = symbol
        self.properties = properties
    def takeGravityIntoAccount(self, otherAsteroids):
        self.accel_x = 0
        self.accel_y = 0
        for asteroid in otherAsteroids:
            if("emitsGravity" in asteroid.properties and asteroid != self):
                m = asteroid.mass
                r = dist((self.x,self.y),(asteroid.x,asteroid.y))
                accelVector = getDirectionVector((self.x,self.y) , (asteroid.x,asteroid.y) , m / r)
                self.accel_x += accelVector[0]
                self.accel_y += accelVector[1]
    # def takeCollisionsIntoAccount(self, otherAsteroids):
    def stepForward(self, dt=1, otherAsteroids=[]):
        if "affectedByGravity" in self.properties:
            self.takeGravityIntoAccount(otherAsteroids)

        # if "destroysThingsOnCollision" not in self.properties:
        #     self.takeCollisionsIntoAccount(otherAsteroids)
        # x = x_0 + v_0*t + 1/2*a*t^2
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        self.x += self.accel_x * 0.5 * dt**2
        self.y += self.accel_y * 0.5 * dt**2

        #v = v_0 + a*t
        self.vel_x += self.accel_x * dt
        self.vel_y += self.accel_y * dt


#Insertion sort by x position
#Keeping the list of asteroids sorted by x position helps speed up detection of asteroid proximity
#(and collision when/if I get to that)
#Insertion sort is fast for nearly sorted lists
def insertionSort(theList):
    for i in range(1,len(theList)):
        j = i
        while(j > 0 and theList[j].x > theList[j-1].x):
            theList[j-1], theList[j] = theList[j], theList[j-1]
            j -= 1
    return theList

def findJumps(asteroids):
    jumpPositions = []
    lenAsteroids = len(asteroids)
    for i in range(lenAsteroids - 1):
        asteroid = asteroids[i]
        j = i + 1
        while(j < lenAsteroids and asteroids[j][0] - asteroid[0] <= jumpDistance[0]):
            otherAst = asteroids[j]
            if(dist(asteroid,otherAst) <= jumpDistance[0]):
                jumpPositions.append((asteroid,otherAst))
            j += 1
    return jumpPositions

class History: #positions of stuff over time
    def __init__ (self, asteroidData=[], jumpData = [], jumpCounts = [], steps=600,frame = 0):
        self.asteroidData = asteroidData
        self.jumpData = jumpData
        self.jumpCounts = jumpCounts
        self.steps = steps
        self.frame = frame
    def fill(self, board, dt=0.01):
        asteroidData = []
        jumpData = []
        jumpCounts = []
        for i in range(self.steps):
            oldboard = board
            asteroidData.append([])
            jumpData.append([])
            jumpCounts.append(0)
            for ast in board:
                ast.stepForward(dt,oldboard)
            board = sorted(board, key=lambda asteroid : asteroid.x)
            # board = insertionSort(board)
            for ast in board:
                asteroidData[i].append((ast.x,ast.y,ast.symbol))
            jumpData[i] = findJumps(asteroidData[i])
            jumpCounts[i] = len(jumpData[i])
        self.asteroidData = asteroidData
        self.jumpData = jumpData
        self.jumpCounts = jumpCounts
    def frameForward(self, numFrames=1):
        if(numFrames+self.frame < self.steps):
            self.frame += numFrames
    def frameBackward(self, numFrames=1):
        if(self.frame-numFrames >= 0):
            self.frame -= numFrames
    def stuffAtFrame(self):
        return (self.asteroidData[self.frame],self.jumpData[self.frame],self.jumpCounts[self.frame])


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





#procedural generation for asteroids
def seedBoard(board):
    baseVelocity = 0.5
    #Rock at the center
    board.append(Asteroid(symbol='R', mass=6, properties=["emitsGravity"]))
    #gravity test
    board.append(Asteroid(symbol='G',x=5,y=5,vel_x = random.uniform(-3.5*baseVelocity,3.5*baseVelocity), vel_y = random.uniform(-3.5*baseVelocity,3.5*baseVelocity), properties = ['affectedByGravity']))
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
    #finally sort board by x position
    board = sorted(board,key=lambda asteroid : asteroid.x)
    return board



#making the ingame stuff
camera = Cam()
board = []
history = History()

seedBoard(board)
history.fill(board)





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

# def isVisible(pixel, sightRange):
#     if(dist(pixel,[player.x,player.y]) <= sightRange):
#         return True
#     return False

def fillInPossibleJumps(jumpList):
    jumpDisplayPoints = []
    for jump in jumpList:
        asteroid = jump[0]
        otherAst = jump[1]
        mid = midpoint(asteroid,otherAst)
        quarter = midpoint(asteroid,mid)
        threequarters = midpoint(otherAst,mid)
        jumpDisplayPoints.append(mid)
        jumpDisplayPoints.append(quarter)
        jumpDisplayPoints.append(threequarters)
        jumpDisplayPoints.append(midpoint(asteroid,quarter))
        jumpDisplayPoints.append(midpoint(quarter,mid))
        jumpDisplayPoints.append(midpoint(mid,threequarters))
        jumpDisplayPoints.append(midpoint(threequarters,otherAst))
    return jumpDisplayPoints

def printEverything():
    #clear pixels
    for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

    #refill pixels
    stuff = history.stuffAtFrame()
    asteroids = stuff[0]
    jumps = stuff[1]
    jumpCount = stuff[2]


    # if(historyFrame[0] != history.frame):
    #     historyFrame[0] = history.frame
    #     jumps[0] = fillInJumpsFromPos(asteroids[0],asteroids)
    for p in fillInPossibleJumps(jumps):
        pixel = getPixelForPosition(p[0],p[1],camera.x,camera.y,camera.zoomConstant)
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
    print(jumpCount)

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




#main loop
while not gameOver[0]:
    clearScreen()
    printEverything()
    takePlayerInput()
