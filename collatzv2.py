# collatz

valuesSoFar = {1:0}

def iterate(num):
    count = 0
    numsThisLoop = []
    origNum = num
    while (num != 1):
        if num in valuesSoFar:
            count = valuesSoFar[num]
            num = 1
        elif (num % 2 == 0):
            num = num / 2
            numsThisLoop = [num] + numsThisLoop
        else:
            num = 3 * num + 1
            numsThisLoop = [num] + numsThisLoop
    valuesSoFar[origNum] = count + len(numsThisLoop)
    for i in range(0,len(numsThisLoop)):
        valuesSoFar[numsThisLoop[i]] = count + i
    return count + len(numsThisLoop)


highestSoFar = 1
for i in range(1, 100000000):
    iterations = iterate(i)
    if (iterations >= highestSoFar):
        highestSoFar = iterations
        print(i, " reached 1 in ", iterations, " iterations")
