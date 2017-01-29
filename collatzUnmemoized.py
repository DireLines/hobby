# collatz

def iterate(num):
    count = 0
    while (num != 1):
        if (num % 2 == 0):
            num = num / 2
            count += 1
        else:
            num = 3 * num + 1
            count += 1
    return count


highestSoFar = 1
results = {}
for i in range(1, 100000000):
    iterations = iterate(i)
    if (iterations >= highestSoFar):
        highestSoFar = iterations
        print(i, " reached 1 in ", iterations, " iterations")
