
def convert(s, a, b):
    """
    Converts s from base a to base b
    """
    return frm(to(s, a), b)

def frm(x, b):
    """
    Converts given number x, from base 10 to base b
    x -- the number in base 10
    b -- base to convert
    """
    assert(x >= 0)
    assert(1< b < 37)
    r = ''
    import string
    while x > 0:
        r = string.printable[x % b] + r
        x //= b
    return r

def to(s, b):
    """
    Converts given number s, from base b to base 10
    s -- string representation of number
    b -- base of given number
    """
    assert(1 < b < 37)
    return int(s, b)

def iterateNum(num, exp, base):
    num_str = convert(str(num), 10, base)
    sums = []
    loopMembersDec = []
    loopMembersBase = []
    s = 0
    for dig in range(0, len(num_str)):
        if(num_str[dig] == "0"):
            s += 0
        else:
            s += int(convert(num_str[dig],base,10))**exp
    sums.append(s)
    while(s not in loopNums):
        num_str = convert(str(s), 10, base)
        s = 0
        for dig in range(0, len(num_str)):
            if(num_str[dig] == "0"):
                s += 0
            else:
                s += int(convert(num_str[dig],base,10))**exp
        if(s in sums):
            for sumindex in range(sums.index(s), len(sums)):
                loopNums.append(sums[sumindex])
                loopMembersDec.append(sums[sumindex])
                loopMembersBase.append(convert(str(sums[sumindex]), 10, base))
            loopsDec.append(loopMembersDec)
            loopsBase.append(loopMembersBase)
        else:
            sums.append(s)


for exp in range(5,6):
    for base in range(13,14):
        loopNums = []
        loopsDec = []
        loopsBase = []
        for num in range(1,500000):
            iterateNum(num, exp, base)
        print(len(loopsDec), " loops for exponent ", exp, " in base ", base)
        for i in range(0,len(loopsDec)):
            print("loop ", i+1, " : ", loopsDec[i])
            print("loop ", i+1, " expressed in base ", base, " : ", loopsBase[i])
        print(" ")




