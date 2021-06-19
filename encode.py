import argparse

#Setup arguments
parser = argparse.ArgumentParser(description='Create raw mode2 config file from options for sharp AC controller')
parser.add_argument('--temp', metavar='[18-32]', choices=range(18,33), type=int, nargs='?',
                    help='an integer tempreture 18-32 degrees (only applies for heat and cool, default 23)', default=23)
parser.add_argument('--mode', metavar='[0-4]', choices=range(0,5), type=int, nargs='?',
                    help='Which mode? 0 = auto, 1 = heat, 2 = cool, 3 = dehumidify, 4 = fan', required=True)
parser.add_argument('--autotemp', metavar='[0-4]', choices=range(0,5), type=int, nargs='?',
                    help='which level of heating/cooling? 0 = off, 1 = coldest, 2 = cold, 3 = hot, 4 = hottest (only applies to auto and dehumidify modes, defaults to off)', default=0)
parser.add_argument('--speed', metavar='[0-3]', choices=range(0,4), type=int, nargs='?',
                    help='Which Fan Speed? 0 = auto, 1 = slow, 2 = medium, 3 = fast (auto not available in fan mode, defaults to slow)', default=1)
parser.add_argument('--power', metavar='[0-2]', choices=range(0,3), type=int, nargs='?',
                    help='Which command? 0 = off, 1 = on, 2 = update only', required=True)
parser.add_argument('--swing', default=False, action='store_true', help='Change swing setting?')


args = parser.parse_args()

#setup AC values
pulse = "435"
spaceShort = "1620"
spaceLong = "3700"
spaceSeperator = "20000"

# gap before transmission is not Bit Flipped
codeGap = "000"

# Setup code to binary mappings
tempMappings = { "0" : "1111", "18" : "1110", "19" : "1101", "20" : "1100", "21" : "1011", "22" : "1010", "23" : "1001", "24" : "1000", "25" : "0111", "26" : "0110", "27" : "0101", "28" : "0100", "29" : "0011", "30" : "0010", "31" : "0001", "32" : "0000" }
modeMappings = { "0" : "111", "1" : "110", "2" : "101", "3" : "100", "4" : "011"}
autotempMappings = { "0" : "111", "1" : "001", "2" : "010", "3" : "110", "4" : "101"}
fanMappings = {"0" : "111", "1" : "110", "2" : "100", "3" : "010"}
powerMappings = {"0" : "101", "1" : "110", "2" : "100"}

modeNames = { "0" : "auto", "1" : "heat", "2" : "cool", "3" : "dehu", "4" : "fan"}
autotempNames = { "0" : "aTmpNorm", "1" : "aTmpCold2", "2" : "aTmpCold1", "3" : "aTmpHot1", "4" : "aTmpHot2"}
fanNames = {"0" : "speedA", "1" : "speed1", "2" : "speed2", "3" : "speed3"}
powerNames = {"0" : "off", "1" : "on", "2" : "upd"}
swingNames = {"0" : "", "1" : "swing"}

# setup static values depending on mode to match original controller output
if args.mode == 0: # === auto ===
	args.temp = 0 # auto mode, so no temp - special case for auto mode only
elif args.mode == 1: # === heat ===
	args.autotemp = 0 # autoTemp does not apply in heat mode
elif args.mode == 2: # === cool ===
	args.autotemp = 0 # autoTemp does not apply in cool mode
elif args.mode == 3: # === dehumidify ===
    args.temp = 18 # no temp configurable, set to 18 as per remote output
elif args.mode == 4: # === fan ===
	args.autotemp = 0 # autoTemp does not apply in fan mode
    args.temp = 18 # no temp configurable, set to 18 as per remote output
    if args.speed == 0 : args.speed = 1 # we cant have auto fan in fan mode

if args.swing == True: #cannot invoke swing with on/off command
	args.power = 2


# Turn options into binary code
def buildBinary():
	# build start
	builder = "01"
	# build auto/dehumidifier temp code
	builder += autotempMappings.get(f"{args.autotemp}")
	# build temp
	builder += tempMappings.get(f"{args.temp}")
	# stop digit
	builder += "1"
	# then mode code
	builder += modeMappings.get(f"{args.mode}")
	# stop digit
	builder += "1"
	# fan speed
	builder += fanMappings.get(f"{args.speed}")
	# filler stuff - probably timer
	builder += "11111"
	# change swing command
	builder += "0001" if args.swing else "1111"
	# turn on / off / update command
	builder += powerMappings.get(f"{args.power}")
	return builder

# Finalize binary with a decoration (start,seperator,bit flip)
def decorateBinary(binary):
	builder = codeGap + binary + "|"
	invertedBinary = ""
	for i, v in enumerate(binary):
		invertedBinary += "0" if v == "1" else "1"
	builder += codeGap + invertedBinary + "|"
	builder += codeGap + binary
	return builder


# Encode to Raw codes like mode2 output
def encodeRawCodes(code):
	
	count = 0
	#name of code
	powerN = powerNames.get(f"{args.power}")
	modeN = modeNames.get(f"{args.mode}")
	fanN = fanNames.get(f"{args.speed}")
	autotempN = autotempNames.get(f"{args.autotemp}")
	tempN = f"{args.temp}"
	swingN = "_swing\n" if args.swing else "\n"
	builder = "name key_"+powerN+"_"+modeN+"_"+autotempN+"_"+fanN+"_"+tempN+swingN

	#build final raw codes
	for i, v in enumerate(code):
		count += 1
		builder += "      " + pulse
		if v != '|':
			if v == "0":
				builder += "     " + spaceShort
			else:
				builder += "     " + spaceLong
		else:
			builder += "    " + spaceSeperator + "\n"
		if count >= 3:
			builder += "\n"
			count = 0
			
	builder += "      " + pulse + "\n"
	return builder

binary = buildBinary()
#print(binary)
decorated = decorateBinary(binary)
#print("")
#print(decorated)
rawCodes = encodeRawCodes(decorated)
#print("")
print(rawCodes)