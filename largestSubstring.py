#
#                       labrador
#                       adorlablabbrado
#
#

def largestSubstring(one,two):
    if(len(one) > len(two)):
        tmp = one
        one = two
        two = tmp
    #now two is larger or same size as one
    longest = ''
    longestLength = 0
    i = 0
    lenOne = len(one)
    lenTwo = len(two)
    while(i < lenOne):
        j = 0
        while(j < lenTwo-longestLength):
            if(one[i] == two[j]):
                k = j+1
                l = i+1
                thisLength = 1
                while(k < lenTwo and l < lenOne and one[l] == two[k]):
                    thisLength += 1
                    k += 1
                    l += 1
                if(thisLength > longestLength):
                    longestLength = thisLength
                    longest = one[i:l]
            j += 1
        i += 1
    return longest

theString = ''
for i in range(100000):
    theString = largestSubstring("labrador","larbador")
print(theString)

