#perspective drawing ASCII
import math

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
points = [[0,0,0,'A'],[1,0,0,'B'],[0,1,0,'A'],[0,0,1,'A'],[1,1,0,'B'],[1,0,1,'B'],[0,1,1,'A'],[1,1,1,'B'],[0.5,0.4,0.3,'C']]

#all info related to player position and orientation.
#TODO make player orientation actually work
playerPos = [-3,0,0]
#playerFacing = [1,0,0]
#pivotAngle = 0


#given player position and orientation, figures out what a point in space "looks like" in the player's apparent coordinate system in which x axis is forward, z is upward and y is left-right
#TODO everything
#def getApparentXYZ(absoluteXYZ, playerXYZ, facingVector, pivotAngle):


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

    r = zoomConstant * math.atan2(math.sqrt(deltaY ** 2 + deltaZ ** 2), deltaX)

    x = r * math.cos(math.atan2(deltaZ, deltaY))
    y = r * math.sin(math.atan2(deltaZ, deltaY))

    return (x,y, deltaX)

#clears the display and then renders all the points. At the moment, points mapping to the same pixel will just overwrite previous values, regardless of which is closer to the player.
#TODO make pixels render only if they are closer than previous pixel.
def printEverything():
    for x in range(leftBound, rightBound):
        for y in range(bottomBound, topBound):
            pixels[(x, y)] = ' '

    for point in points:
        xy = getXY(point, playerPos, zoomConstant)
        #print(xy)
        if(xy[2] > 0):
            dispX = int(round(xy[0]))
            dispY = int(round(xy[1]))
            #print(dispX, dispY)
            if(math.fabs(dispX) <= rightBound and math.fabs(dispY) <= topBound):
                pixels[(dispX, dispY)] = point[3]
    rows = []
    pixels[(0,0)] = '+'
    for y in range(bottomBound, topBound):
        thisRow = ''
        for x in range(leftBound, rightBound):
            thisRow = thisRow + pixels[(x,y)]
        print(thisRow)



#waits for player input such as movement/rotation
#TODO add quit button, add rotation controls once getApparentXYZ is working
def takePlayerInput():
    theInput = input()
    if theInput == 'w':
        playerPos[0] += 0.5
    if theInput == 's':
        playerPos[0] -= 0.5
    if theInput == 'a':
        playerPos[1] -= 0.5
    if theInput == 'd':
        playerPos[1] += 0.5
    if theInput == 'q':
        playerPos[2] -= 0.5
    if theInput == 'e':
        playerPos[2] += 0.5


#game loop
gameOver = False
while gameOver == False:
    printEverything()
    takePlayerInput()

