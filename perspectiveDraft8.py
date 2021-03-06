#perspective drawing ASCII
import math
import numpy as np
import subprocess

#setting up ACSII display stuff
pixelAspectRatio = 2.0 #this is the ratio height / width for one character of text in whatever terminal you're using. Will make it adjust to different terminals later.
screenAspectRatio = 1.2 #this is the ratio height / width for the whole screen
screenWidth = 112
screenHeight = int((screenAspectRatio*screenWidth) / pixelAspectRatio)
leftBound = int(-screenWidth / 2)
rightBound = int(screenWidth / 2)
topBound = int(screenHeight / 2)
bottomBound = int(-screenHeight / 2)
zoomConstant = 40
pixels = {}
pixelsRendered = []
for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

#points in 3d space to be rendered. The last value in each point is what character will represent it in the display
points = []

#rotation matrix. Will be updated whenever player rotates
rot = [np.array([[0,0,0],
                 [0,0,0],
                 [0,0,0]])]

#all info related to player position and orientation.
playerPos = [0,0,0]
yawpitchroll = [0,0,0]

playerStep = 0.1
playerRotate = 3
playerRotate = math.radians(playerRotate)
playerRotationChanged = [True]

#main loop status
gameOver = [False]

#If the pixel at X,Y already contains a thing, return the index of the 3d coordinates of that thing
#otherwise return -1
def pixelsRenderedIndex(x,y):
    for i in range(0,len(pixelsRendered)):
        if(pixelsRendered[i][3] == x and pixelsRendered[i][4] == y):
            return i
    return -1

#3d Euclidean distance. Always good to have around
def dist3d(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    dz = point2[2] - point1[2]

    underSqrt = dx**2 + dy**2 + dz**2
    return math.sqrt(underSqrt)

#makes sure player orientation angles stay between 0 and 360 degrees
def clipAngles():
    threesixty = math.radians(360)
    if yawpitchroll[0] >= threesixty or yawpitchroll[0] < 0:
        yawpitchroll[0] = yawpitchroll[0] % threesixty
    if yawpitchroll[1] >= threesixty or yawpitchroll[1] < 0:
        yawpitchroll[1] = yawpitchroll[1] % threesixty
    if yawpitchroll[2] >= threesixty or yawpitchroll[2] < 0:
        yawpitchroll[2] = yawpitchroll[2] % threesixty


#remakes rotation matrix whenever player rotation is updated
def updateRotationMatrix():
    yaw = yawpitchroll[0]
    pitch = yawpitchroll[1]
    roll = yawpitchroll[2]

    zrot = np.array([[math.cos(yaw) ,-math.sin(yaw) , 0],
                    [math.sin(yaw)  ,math.cos(yaw)  , 0],
                    [0              , 0             , 1]])

    yrot = np.array([[math.cos(roll), 0, math.sin(roll)],
                    [0              , 1             , 0],
                    [-math.sin(roll), 0, math.cos(roll)]])
    
    xrot = np.array([[1             , 0               , 0],
                    [0, math.cos(pitch), -math.sin(pitch)],
                    [0, math.sin(pitch), math.cos(pitch)]])

    rot[0] = np.dot(np.dot(zrot, yrot), xrot)

#given player position and orientation, figures out what a point in space "looks like" 
#in the player's apparent coordinate system in which x axis is forward, z is upward and y is left-right
def getApparentXYZ(absoluteXYZ, playerXYZ):
    if playerRotationChanged[0]:
        updateRotationMatrix()
        playerRotationChanged[0] = False
    deltaX = [absoluteXYZ[0] - playerXYZ[0]]
    deltaY = [absoluteXYZ[1] - playerXYZ[1]]
    deltaZ = [absoluteXYZ[2] - playerXYZ[2]]
    deltaXYZ = np.array([deltaX,
                        deltaY,
                        deltaZ])

    apparentXYZ = np.dot(rot[0], deltaXYZ)
    return apparentXYZ

#given player orientation, figures out what a point in space that "looks like" apparentXYZ in the player's coordinate system would be in the official coordinate system
def getAbsoluteXYZ(apparentXYZ):
    #NOTE NEGATIVE SIGNS. This means the matrix generated is the inverse of the rotation matrix
    yaw = -yawpitchroll[0]
    pitch = -yawpitchroll[1]
    roll = -yawpitchroll[2]
    deltaX = [apparentXYZ[0]]
    deltaY = [apparentXYZ[1]]
    deltaZ = [apparentXYZ[2]]
    deltaXYZ = np.array([deltaX,
                        deltaY,
                        deltaZ])

    zrot = np.array([[math.cos(yaw) ,-math.sin(yaw) , 0],
                    [math.sin(yaw)  ,math.cos(yaw)  , 0],
                    [0              , 0             , 1]])

    yrot = np.array([[math.cos(roll), 0, math.sin(roll)],
                    [0              , 1             , 0],
                    [-math.sin(roll), 0, math.cos(roll)]])
    
    xrot = np.array([[1             , 0               , 0],
                    [0, math.cos(pitch), -math.sin(pitch)],
                    [0, math.sin(pitch), math.cos(pitch)]])

    #NOTE matrices are multiplied in REVERSE ORDER from how they are multiplied to get apparentXYZ
    unrot = np.dot(np.dot(xrot, yrot), zrot)


    absoluteXYZ = np.dot(unrot, deltaXYZ)

    return absoluteXYZ


#given a point's apparent coordinates, maps to a point in 2d space.
def getXY(apparentXYZ, zoomConstant):
    deltaX = apparentXYZ[0]
    deltaY = apparentXYZ[1]
    deltaZ = apparentXYZ[2]
    # print("deltaX",deltaX)
    # print("deltaY",deltaY)
    # print("deltaZ",deltaZ)
    r = zoomConstant * math.atan2(math.sqrt(deltaX ** 2 + deltaZ ** 2), deltaY)

    x = r * math.cos(math.atan2(deltaZ, deltaX))
    y = r * math.sin(math.atan2(deltaZ, deltaX))
    #print("XY:",x,y)
    return (x,y, deltaY)

#clears the display and then renders all the points. At the moment, points mapping to the same pixel will just overwrite previous values, regardless of which is closer to the player.
def printEverything():
    #clear board
    for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '
    del pixelsRendered[:]

    #find XY representations of points, puts them on appropriate pixels
    for point in points:
        appxyz = getApparentXYZ(point,playerPos)
        xy = getXY(appxyz, zoomConstant)
        if(xy[2] > 0):
            dispX = int(round(xy[0]*pixelAspectRatio))
            dispY = int(round(xy[1])) #I just happen to be using a terminal with a 2:1 aspect ratio for text characters.
            #Will make this work for any aspect ratio later.
            if(math.fabs(dispX) < rightBound and math.fabs(dispX) >= leftBound 
            and math.fabs(dispY) >= bottomBound and math.fabs(dispY) < topBound):
                overwriteIndex = pixelsRenderedIndex(dispX,dispY)
                if overwriteIndex == -1:
                    pixels[(dispX, dispY)] = point[3]
                    pixelsRendered.append([point[0],point[1],point[2],dispX,dispY])
                elif dist3d(point,playerPos) < dist3d(pixelsRendered[overwriteIndex],playerPos):
                        pixels[(dispX, dispY)] = point[3]
                        pixelsRendered[overwriteIndex][0] = point[0]
                        pixelsRendered[overwriteIndex][1] = point[1]
                        pixelsRendered[overwriteIndex][2] = point[2]



    #put crosshair in center of screen
    #TODO replace this with a function called renderHUD()
    pixels[(0,0)] = '+'

    #prints row by row
    for y in reversed(range(bottomBound, topBound)):
        thisRow = ''
        for x in range(leftBound, rightBound):
            thisRow = thisRow + pixels[(x,y)]
        print(thisRow)

#functions defining player movement in terms of player's reference frame
def movePlayer(x,y,z):
    absXYZ = getAbsoluteXYZ([x,y,z])
    playerPos[0] += absXYZ[0][0]
    playerPos[1] += absXYZ[1][0]
    playerPos[2] += absXYZ[2][0]

# def rotatePlayer(yaw,pitch,roll):
#     absXYZ = getAbsoluteXYZ([yaw,pitch,roll])
#     yawpitchroll[0] += absXYZ[0][0]
#     yawpitchroll[1] += absXYZ[1][0]
#     yawpitchroll[2] += absXYZ[2][0]


#debugging stuff. might eventually be important for object creation
def makeAPoint():
    print("X:")
    newX = float(input())
    print("Y:")
    newY = float(input())
    print("Z:")
    newZ = float(input())
    print("Symbol:")
    newSymbol = input()
    addPoint(newX,newY,newZ,newSymbol)

def addPoint(x, y, z, symbol):
    symbolChar = symbol[0]
    points.append([x,y,z,symbolChar])

def printPlayerInfo():
    print("         (x,y,z): (",playerPos[0],",",playerPos[1],",",playerPos[2],")")
    print("(yaw,pitch,roll): (",math.degrees(yawpitchroll[0]),",",math.degrees(yawpitchroll[1]),",",math.degrees(yawpitchroll[2]),")")

#control listing
def printHelp():
    print("w - move forward")
    print("a - move left")
    print("s - move backward")
    print("d - move right")
    print("q - move down")
    print("e - move up")
    print("")
    print("o - rotate up")
    print("k - face left")
    print("l - rotate down")
    print("; - face right")
    print("i - tilt counterclockwise")
    print("p - tilt clockwise")
    print("")
    print("x - quit")
    print("m - make a point")

#live input a single character
class Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = GetchWindows()
        except ImportError:
            self.impl = GetchUnix()

    def __call__(self): return self.impl()


class GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

#waits for player input such as movement/rotation
def takePlayerInput():
    print("h - help")

    theInput = Getch().__call__()

    #misc
    if theInput == 'm':
        makeAPoint()
        return
    if theInput == 'x':
        gameOver[0] = True
        return
    if theInput == 'h':
        printHelp()
        takePlayerInput()

    # TODO make player rotation relative to player's reference frame instead of global xyz, put these in takePlayerInput()

    #translation
    if theInput == 'w':
        movePlayer(0,playerStep,0)
    if theInput == 's':
        movePlayer(0,-playerStep,0)
    if theInput == 'a':
        movePlayer(-playerStep,0,0)
    if theInput == 'd':
        movePlayer(playerStep,0,0)
    if theInput == 'q':
        movePlayer(0,0,-playerStep)
    if theInput == 'e':
        movePlayer(0,0,playerStep)

    # #rotation
    # if theInput == 'o':
    #     rotatePlayer(0,-playerRotate,0)
    #     playerRotationChanged[0] = True
    # if theInput == 'l':
    #     rotatePlayer(0,playerRotate,0)
    #     playerRotationChanged[0] = True
    # if theInput == 'k':
    #     rotatePlayer(-playerRotate,0,0)
    #     playerRotationChanged[0] = True
    # if theInput == ';':
    #     rotatePlayer(playerRotate,0,0)
    #     playerRotationChanged[0] = True
    # if theInput == 'i':
    #     rotatePlayer(0,0,-playerRotate)
    #     playerRotationChanged[0] = True
    # if theInput == 'p':
    #     rotatePlayer(0,0,playerRotate)
    #     playerRotationChanged[0] = True


    #rotation
    if theInput == 'o':
        yawpitchroll[1] -= playerRotate
        playerRotationChanged[0] = True
    if theInput == 'l':
        yawpitchroll[1] += playerRotate
        playerRotationChanged[0] = True
    if theInput == 'k':
        yawpitchroll[0] -= playerRotate
        playerRotationChanged[0] = True
    if theInput == ';':
        yawpitchroll[0] += playerRotate
        playerRotationChanged[0] = True
    if theInput == 'i':
        yawpitchroll[2] -= playerRotate
        playerRotationChanged[0] = True
    if theInput == 'p':
        yawpitchroll[2] += playerRotate
        playerRotationChanged[0] = True

def clearTerm():
    subprocess.call(["clear"])

addPoint(0,0,0,'A')
addPoint(1,0,0,'B')
addPoint(0,1,0,'A')
addPoint(0,0,1,'A')
addPoint(1,1,0,'B')
addPoint(1,0,1,'B')
addPoint(0,1,1,'A')
addPoint(1,1,1,'B')
addPoint(0.5,0.4,0.3,'C')
addPoint(0,3,0,'o')

clearTerm()
#main loop
while not gameOver[0]:
    clipAngles()
    printEverything()
    printPlayerInfo()
    takePlayerInput()
    clearTerm()
