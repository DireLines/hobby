base = 11
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

for base in range (2, 37):
    print(base)
    for num in range(0,500000):
        num_str = convert(str(num), 10, base)
        s = 0
        for dig in range(0, len(num_str)):
            if(num_str[dig] == "0"):
                s += 0
            else:
                s += int(convert(num_str[dig],base,10))**int(convert(num_str[dig],base,10))
        if(s == num):
            print(convert(str(num), 10, base))
            print("Decimal: ", num)
    print(" ")