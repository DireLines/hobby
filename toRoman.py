# decimal to Roman numeral converter. works up to 3999, at which point you run out of symbols.
print("number: ")

num = int(input())
roman = ""

suffixes = [
	["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"],
	["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"],
	["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "DM"],
	["", "M", "MM", "MMM"]
	]


numLength = len(str(num))

if(num < 4000):
	for val in range(0, numLength):
		digit = int((num % (10 ** (val + 1))) / (10 ** val))
		roman = suffixes[val][digit] + roman
	print (roman)
	
else:
    print ("too big")