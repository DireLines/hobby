import asciiRenderer as ar
import math

#distance from origin
def mag(point):
    return math.sqrt(point[0]*point[0] + point[1]*point[1])

points = []
pointStep = 0.01
iterations = 30
left = -2
right = 1
top = 1
bottom = -1

re = left
im = top

while(re <= right):
    while(im >= bottom):
        point = [re,im]
        a = re
        b = im
        i = 0
        for i in range(iterations):
            #square
            tmp = a
            a = a*a - b*b
            b = 2*tmp*b
            #add original
            a += re
            b += im
            if(mag([a,b]) > 2):
                break
        if(mag([a,b]) <= 2):
            points.append(point)
        im -= pointStep
    im = top
    re += pointStep


ar.render(points)