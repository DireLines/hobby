import math
import itertools
num = 1064

primes = [2]
def isPrime(num):
    for i in range(2,int(math.sqrt(num))+1):
        if num / i == math.floor(num / i):
            return False
    return True


def getPrimeFactors(num):
    primeFactors = []
    if(num in primes or isPrime(num)):
        if(num not in primes):
            primes.append(num)
        primeFactors.append(num)
        return primeFactors
    for i in range(2,int(math.sqrt(num)+1)):
        if num / i == math.floor(num/i):
            j = int(num / i)
            if(i in primes or isPrime(i)):
                if(i not in primes):
                    primes.append(i)
                primeFactors.append(i)
                if(j in primes or isPrime(j)):
                    if(j not in primes):
                        primes.append(j)
                    primeFactors.append(j)
                    return primeFactors
                else:
                    subfactors = getPrimeFactors(j)
                    for subfactor in subfactors:
                        primeFactors.append(subfactor)
                    return primeFactors
            elif(j in primes or isPrime(j)):
                if(j not in primes):
                    primes.append(j)
                primeFactors.append(j)
                subfactors = getPrimeFactors(i)
                for subfactor in subfactors:
                    primeFactors.append(subfactor)
                return primeFactors
            else:
                subfactorsI = getPrimeFactors(i)
                subfactorsJ = getPrimeFactors(j)
                for subfactorI in subfactorsI:
                    primeFactors.append(subfactorI)
                for subfactorJ in subfactorsJ:
                    primeFactors.append(subfactorJ)
                return primeFactors

def getDistinctPrimeFactors(num):
    primeFactors = []
    if(num in primes or isPrime(num)):
        if(num not in primes):
            primes.append(num)
        primeFactors.append(num)
        trimDuplicates(primeFactors)
        return primeFactors
    for i in range(2,int(math.sqrt(num)+1)):
        if num / i == math.floor(num/i):
            j = int(num / i)
            if(i in primes or isPrime(i)):
                if(i not in primes):
                    primes.append(i)
                primeFactors.append(i)
                if(j in primes or isPrime(j)):
                    if(j not in primes):
                        primes.append(j)
                    primeFactors.append(j)
                    trimDuplicates(primeFactors)
                    return primeFactors
                else:
                    subfactors = getPrimeFactors(j)
                    for subfactor in subfactors:
                        primeFactors.append(subfactor)
                    trimDuplicates(primeFactors)
                    return primeFactors
            elif(j in primes or isPrime(j)):
                if(j not in primes):
                    primes.append(j)
                primeFactors.append(j)
                subfactors = getPrimeFactors(i)
                for subfactor in subfactors:
                    primeFactors.append(subfactor)
                trimDuplicates(primeFactors)
                return primeFactors
            else:
                subfactorsI = getPrimeFactors(i)
                subfactorsJ = getPrimeFactors(j)
                for subfactorI in subfactorsI:
                    primeFactors.append(subfactorI)
                for subfactorJ in subfactorsJ:
                    primeFactors.append(subfactorJ)
                trimDuplicates(primeFactors)
                return primeFactors

def getProperDivisors(num):
    properDivisors = []
    properDivisors.append(1)
    primeFactors = getPrimeFactors(num)
    for chooseNum in range(1, len(primeFactors)):
        for factorCombination in itertools.combinations(primeFactors, chooseNum):
            product = 1
            for factor in factorCombination:
                product *= int(factor)
            properDivisors.append(product)
    dindex = 1
    while(dindex < len(properDivisors)):
        if properDivisors.index(properDivisors[dindex]) != dindex:
            properDivisors.remove(properDivisors[dindex])
        else:
            dindex += 1
    return properDivisors

def trimDuplicates(inList):
    theIndex = 1
    while(theIndex < len(inList)):
        if inList.index(inList[theIndex]) != theIndex:
            inList.remove(inList[theIndex])
        else:
            theIndex += 1


def getAliquotEndpoint(num, iterations):
    s = 0
    if(num != 0):
        if num == 1:
            s = 0
        else:
            divisors = getProperDivisors(num)
            for divisor in divisors:
                s += divisor
        #print(s)
    n = 0
    while(s != 0 and n < iterations):
        n += 1
        if s == 1:
            s = 0
        else:
            divisors = getProperDivisors(s)
            s = 0
            for divisor in divisors:
                s += divisor
        #print(s)
    return s

def getAliquotSequence(num, iterations):
    s = 0
    out = []
    if(num != 0):
        if num == 1:
            s = 0
        else:
            divisors = getProperDivisors(num)
            for divisor in divisors:
                s += divisor
        out.append(s)
    n = 0
    while(s != 0 and n < iterations):
        n += 1
        if s == 1:
            s = 0
        else:
            divisors = getProperDivisors(s)
            s = 0
            for divisor in divisors:
                s += divisor
        out.append(s)
    return out


#print(getAliquotSequence(1080,50))

# highestSoFar = 1
# for num in range(0,500001):
#     if(len(getDistinctPrimeFactors(num)) > highestSoFar):
#         highestSoFar = len(getDistinctPrimeFactors(num))
#         print(num, ":", len(getDistinctPrimeFactors(num)), ":", getDistinctPrimeFactors(num))



# for num in range(40000100,40000200):
#     print(getPrimeFactors(num))


# for num in range(0,1001):
#     aep = getAliquotEndpoint(num,50)
#     if(aep != 0):
#         print(num,":",aep)

    
