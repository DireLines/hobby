import math
import itertools
num = 360

primes = [2,3,5,7,11,13,17,19]
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

print(getPrimeFactors(24))