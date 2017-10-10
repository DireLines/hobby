import sys
q = chr(34)
nl = chr(10)
c = chr(44)
strings = [
"import sys",
"q = chr(34)",
"nl = chr(10)",
"c = chr(44)",
"strings = [",
"]",
"for num in range(0,5):",
"    sys.stdout.write(strings[num] + nl)",
"for num in range(0,len(strings) - 1):",
"    sys.stdout.write(q + strings[num] + q + c + nl)",
"sys.stdout.write(q + strings[len(strings) - 1] + q + nl)",
"for num in range(5,len(strings)):",
"    sys.stdout.write(strings[num] + nl)"
]
for num in range(0,5):
    sys.stdout.write(strings[num] + nl)
for num in range(0,len(strings) - 1):
    sys.stdout.write(q + strings[num] + q + c + nl)
sys.stdout.write(q + strings[len(strings) - 1] + q + nl)
for num in range(5,len(strings)):
    sys.stdout.write(strings[num] + nl)