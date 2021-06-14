import sys


gap = 434
short = 1620
long = 3700
margin = 150
seperator = 20000

def marginCheck(val,type):
	if int(val)<type-margin or int(val)>type+margin:
		return False
	return True

# at the end of the transmission make a new line to seperate them
def newlineTest(val):
	if val % 3 == 0:
		print("")

try:
	count = 1
	block = 0
	for line in sys.stdin:
	#	sys.stdout.write("   " + line)
		result = line.split(" ")


		if result[0] == "pulse" :
			if not marginCheck(result[1],gap):
				print("E",end='')
				continue 
			print("",end='')
			continue

		#seperate blocks
		if count % 3 == 0:
			print(" ",end='')
		count = count + 1


		if result[0] == "space":
			if marginCheck(result[1],short):
				print("0",end='')
				continue
			if marginCheck(result[1],long):
				print("1",end='')
				continue
			if marginCheck(result[1],seperator):
				print("|")
				block = block + 1
				newlineTest(block)
				continue
			#print(result[1],end='')
		if result[0] == "timeout":
				print("*")
				block = block + 1
				newlineTest(block)


except KeyboardInterrupt:
	sys.exit(0) # or 1, or whatever