#perspective drawing ASCII
import math
import numpy as np

#setting up ACSII display stuff
pixelAspectRatio = 2.0 #this is the ratio height / width for one character of text in whatever terminal you're using. Will make it adjust to different terminals later.
screenAspectRatio = 1.2 #this is the ratio height / width for the whole screen
screenWidth = 100
screenHeight = int((screenAspectRatio*screenWidth) / pixelAspectRatio)
leftBound = int(-screenWidth / 2)
rightBound = int(screenWidth / 2)
topBound = int(screenHeight / 2)
bottomBound = int(-screenHeight / 2)
zoomConstant = 40
pixels = {}
for x in range (leftBound, rightBound):
    for y in range (bottomBound, topBound):
        pixels[(x,y)] = ' '

#points in 3d space to be rendered. The last value in each point is what character will represent it in the display
points = []

#all info related to player position and orientation.
playerPos = [0,0,0]
yawpitchroll = [0,0,0]

playerStep = 0.25
playerRotate = 15

#main loop status
gameOver = False

#3d Euclidean distance. Always good to have around
def dist3d(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    dz = point2[2] - point1[2]

    underSqrt = dx**2 + dy**2 + dz**2
    return math.sqrt(underSqrt)

#given player position and orientation, figures out what a point in space "looks like" in the player's apparent coordinate system in which x axis is forward, z is upward and y is left-right
def getApparentXYZ(absoluteXYZ, playerXYZ, yawpitchroll):
    yaw = yawpitchroll[0]
    pitch = yawpitchroll[1]
    roll = yawpitchroll[2]
    deltaX = [absoluteXYZ[0] - playerXYZ[0]]
    deltaY = [absoluteXYZ[1] - playerXYZ[1]]
    deltaZ = [absoluteXYZ[2] - playerXYZ[2]]
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
    rot = np.dot(np.dot(zrot, yrot), xrot)

    apparentXYZ = np.dot(rot, deltaXYZ)
    return apparentXYZ




#given a point's apparent coordinates, maps to a point in 2d space.
def getXY(apparentXYZ, zoomConstant):
    deltaX = apparentXYZ[0]
    deltaY = apparentXYZ[1]
    deltaZ = apparentXYZ[2]
    r = zoomConstant * math.atan2(math.sqrt(deltaX ** 2 + deltaZ ** 2), deltaY)

    x = r * math.cos(math.atan2(deltaZ, deltaX))
    y = r * math.sin(math.atan2(deltaZ, deltaX))
    return (x,y, deltaY)

#clears the display and then renders all the points. At the moment, points mapping to the same pixel will just overwrite previous values, regardless of which is closer to the player.
#TODO make pixels render only if they are closer than previous pixel.
def printEverything():
    #clear board
    for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

    #find XY representations of points, puts them on appropriate pixels
    for point in points:
        appxyz = getApparentXYZ(point,playerPos,yawpitchroll)
        xy = getXY(appxyz, zoomConstant)
        if(xy[2] > 0):
            dispX = int(round(xy[0]*pixelAspectRatio))
            dispY = int(round(xy[1])) #I just happen to be using a terminal with a 2:1 aspect ratio for text characters.
            #Will make this work for any aspect ratio later.
            if(math.fabs(dispX) <= rightBound and math.fabs(dispX) >= leftBound 
            and math.fabs(dispY) >= bottomBound and math.fabs(dispY) <= topBound):
                pixels[(dispX, dispY)] = point[3]


    #put crosshair in center of screen
    #TODO replace this with a function called renderHUD()
    pixels[(0,0)] = '+'

    #prints row by row
    for y in reversed(range(bottomBound, topBound)):
        thisRow = ''
        for x in range(leftBound, rightBound):
            thisRow = thisRow + pixels[(x,y)]
        print(thisRow)


# TODO make player rotation and translation methods relative to player's reference frame instead of global xyz, put these in takePlayerInput()
#debugging stuff. might eventually be important for object creation
def makeAPoint():
    print("X:")
    newX = float(input())
    print("Y:")
    newY = float(input())
    print("Z:")
    newZ = float(input())
    print("Symbol:")
    newSymbol = input()[0]
    addPoint(newX,newY,newZ,newSymbol)

def addPoint(x, y, z, symbol):
    symbolChar = symbol[0]
    points.append([x,y,z,symbolChar])

def printPlayerInfo():
    print("(x,y,z): (",playerPos[0],",",playerPos[1],",",playerPos[2],")")
    print("(yaw,pitch,roll): (",math.degrees(yawpitchroll[0]),",",math.degrees(yawpitchroll[1]),",",math.degrees(yawpitchroll[2]),")")

#waits for player input such as movement/rotation
#TODO add quit button
def takePlayerInput():
    theInput = input()
    if(len(theInput) > 1):
        theInput = theInput[0]

    #misc
    if theInput == 'm':
        makeAPoint()

    #translation
    if theInput == 'w':
        playerPos[1] += playerStep
    if theInput == 's':
        playerPos[1] -= playerStep
    if theInput == 'a':
        playerPos[0] -= playerStep
    if theInput == 'd':
        playerPos[0] += playerStep
    if theInput == 'q':
        playerPos[2] -= playerStep
    if theInput == 'e':
        playerPos[2] += playerStep

    #rotation
    if theInput == 'o':
        yawpitchroll[1] -= math.radians(playerRotate)
    if theInput == 'l':
        yawpitchroll[1] += math.radians(playerRotate)
    if theInput == 'k':
        yawpitchroll[0] -= math.radians(playerRotate)
    if theInput == ';':
        yawpitchroll[0] += math.radians(playerRotate)
    if theInput == 'i':
        yawpitchroll[2] -= math.radians(playerRotate)
    if theInput == 'p':
        yawpitchroll[2] += math.radians(playerRotate)


addPoint(0,1,1,'P')
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

#main loop
while not gameOver:
    printEverything()
    printPlayerInfo()
    takePlayerInput()