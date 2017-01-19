#perspective drawing ASCII
import math
import numpy as np

#setting up ACSII display stuff
screenWidth = 100
screenHeight = 60
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
points = [[0,0,0,'A'],[1,0,0,'B'],[0,1,0,'A'],[0,0,1,'A'],[1,1,0,'B'],[1,0,1,'B'],[0,1,1,'A'],[1,1,1,'B'],[0.5,0.4,0.3,'C'],[0,3,0,'o']]

#all info related to player position and orientation.
playerPos = [0,0,0]
yawpitchroll = [0,0,0]

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



    zrot = np.array([[math.cos(yaw),-math.sin(yaw),0],
                    [math.sin(yaw),math.cos(yaw),0],
                    [0,0,1]])
    yrot = np.array([[math.cos(roll), 0, math.sin(roll)],
                    [0, 1, 0],
                    [-math.sin(roll), 0, math.cos(roll)]])
    xrot = np.array([[1, 0, 0],
                    [0, math.cos(pitch), -math.sin(pitch)],
                    [0, math.sin(pitch), math.cos(pitch)]])
    rot = np.dot(np.dot(zrot, yrot), xrot)
    inverseRot = np.linalg.inv(rot)

    apparentXYZ = np.dot(inverseRot, deltaXYZ)
    return apparentXYZ




#given a point's apparent coordinates, maps to a point in 2d space.
def getXY(apparentXYZ, playerXYZ, zoomConstant):
    appX = apparentXYZ[0]
    appY = apparentXYZ[1]
    appZ = apparentXYZ[2]
    playerX = playerXYZ[0]
    playerY = playerXYZ[1]
    playerZ = playerXYZ[2]
    deltaX = appX - playerX
    deltaY = appY - playerY
    deltaZ = appZ - playerZ

    r = zoomConstant * math.atan2(math.sqrt(deltaX ** 2 + deltaZ ** 2), deltaY)

    x = r * math.cos(math.atan2(deltaZ, deltaX))
    y = r * math.sin(math.atan2(deltaZ, deltaX))

    return (x,y, deltaY)

#clears the display and then renders all the points. At the moment, points mapping to the same pixel will just overwrite previous values, regardless of which is closer to the player.
#TODO make pixels render only if they are closer than previous pixel. Make rows print in correct order.
def printEverything():
    for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

    for point in points:
        appxyz = getApparentXYZ(point,playerPos,yawpitchroll)
        xy = getXY(appxyz, playerPos, zoomConstant)
        if(xy[2] > 0):
            dispX = int(round(xy[0]))
            dispY = int(round(xy[1]))
            if(math.fabs(dispX) <= rightBound and math.fabs(dispY) <= topBound):
                pixels[(dispX, dispY)] = point[3]
    pixels[(0,0)] = '+'
    rows = []
    for y in range(bottomBound, topBound):
        thisRow = ''
        for x in range(leftBound, rightBound):
            thisRow = thisRow + pixels[(x,y)]
        rows = [thisRow] + rows
    for row in rows:
        print(row)

#TODO make player rotation and translation methods relative to player's reference frame instead of global xyz, put these in takePlayerInput()

#waits for player input such as movement/rotation
#TODO add quit button
def takePlayerInput():
    theInput = input()


    if theInput == 'w':
        playerPos[1] += 0.5
    if theInput == 's':
        playerPos[1] -= 0.5
    if theInput == 'a':
        playerPos[0] -= 0.5
    if theInput == 'd':
        playerPos[0] += 0.5
    if theInput == 'q':
        playerPos[2] -= 0.5
    if theInput == 'e':
        playerPos[2] += 0.5


    if theInput == 'o':
        yawpitchroll[1] += math.radians(15)
    if theInput == 'l':
        yawpitchroll[1] -= math.radians(15)
    if theInput == 'k':
        yawpitchroll[0] -= math.radians(15)
    if theInput == ';':
        yawpitchroll[0] += math.radians(15)
    if theInput == 'i':
        yawpitchroll[2] -= math.radians(15)
    if theInput == 'p':
        yawpitchroll[2] += math.radians(15)



#game loop
gameOver = False
while gameOver == False:
    printEverything()
    takePlayerInput()