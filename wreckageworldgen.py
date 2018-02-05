#wreckageworldgen.py

import math,random
from collections import deque
import asciiRenderer as ar

def randomNoise(seed,percentage,width):
    random.seed(seed)
    result = {}
    for i in range(width):
        for j in range(width):
            rand = random.randint(0,100)
            if rand <= percentage:
                result[(i,j)] = 1
            else:
                result[(i,j)] = 0
    return result

def neighbors(cell):
    x = cell[0]
    y = cell[1]
    neighbors = [
    (x-1,y+1),(x,y+1),(x+1,y+1),
    (x-1,y)  ,        (x+1,y)  ,
    (x-1,y-1),(x,y-1),(x+1,y-1)
    ]
    return neighbors

def runAutomata(grid):
    #first:Wreckage (B5678/S35678) for 45 generations
    birth = [5,6,7,8]
    survival = [3,5,6,7,8]
    for i in range(45):
        previousState = grid
        for p in grid:
            neighborCount = 0
            for neighbor in neighbors(p):
                if neighbor in previousState:
                    neighborCount += previousState[neighbor]

            if(previousState[p] == 0 and neighborCount in birth):
                grid[p] = 1
            elif(previousState[p] == 1):
                if(neighborCount in survival):
                    grid[p] = 1
                else:
                    grid[p] = 0

    #second:Caves (B5678/S45678) for 75 generations
    survival = [4,5,6,7,8]
    for i in range(75):
        previousState = grid
        for p in grid:
            neighborCount = 0
            for neighbor in neighbors(p):
                if neighbor in previousState:
                    neighborCount += previousState[neighbor]

            if(previousState[p] == 0 and neighborCount in birth):
                grid[p] = 1
            elif(previousState[p] == 1):
                if(neighborCount in survival):
                    grid[p] = 1
                else:
                    grid[p] = 0
    return grid

def removeSmallIslandsAndHoles(grid):
    #run flood fill to split grid into islands
    newgrid = {}
    howSmallToRemoveIsland = 180
    howSmallToRemoveHole = 180
    for p in grid:
        if(grid[p] == 0 or grid[p] == 1): #new chunk
            original = grid[p]
            q = []
            q.append(p)
            result = [p]
            while(len(q) > 0):
                p = q.pop(0)
                for neighbor in neighbors(p):
                    if(neighbor in grid and grid[neighbor] == grid[p]):
                        if neighbor not in q:
                            q.append(neighbor)
                            result.append(neighbor)
                grid[p] = 3 # mark as done
            if(original == 0):
                if(len(result) <= howSmallToRemoveHole):
                    for cell in result:
                        newgrid[cell] = 2
                else:
                    # print(original, len(result))
                    for cell in result:
                        newgrid[cell] = 0
            else:
                if(len(result) <= howSmallToRemoveIsland):
                    for cell in result:
                        newgrid[cell] = 0
                else:
                    print(original, len(result))
                    for cell in result:
                        newgrid[cell] = 1
    return newgrid

def clearzeros(grid):
    newgrid = {}
    for p in grid:
        if grid[p] != 0:
            newgrid[p] = grid[p]
    return newgrid

def generate(seed):
    result = randomNoise(seed,55,180)
    result = runAutomata(result)
    result = removeSmallIslandsAndHoles(result)
    result = clearzeros(result)
    return result

theGrid = generate(6453241)
ar.render(theGrid, symbols=True)