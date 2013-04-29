import argparse
parser = argparse.ArgumentParser()
parser.add_argument("inputFile", help = "relative path of the log file")
parser.add_argument('-o', '--output', help = 'output json file (default: converted_log_file.json)')
args = parser.parse_args()


# Open the input log file
try:
	inputFile = open(args.inputFile, 'r')
	if args.output:
		outputFile = open(args.output, 'w+')
	else:
		outputFile = open('converted_log_file.json', 'w+')

	myDict = dict()	
	start_time = None	

	while True:
		line = inputFile.readline()
		if line == '': break		# EOF
		elif line[0] == '#': continue	# Comment
		else:
			line = line.split(';')
			try:
				# !! Order?
				myDict[line[0]] = myDict[line[0]] + [[ int(line[1]) - start_time, int(line[2]) ]]
			except KeyError:
				start_time = int(line[1])
				myDict[line[0]] = [ [ 0, int(line[2]) ] ]

	print myDict
	
	outputFile.write('[\n')
	keys = myDict.keys()
	for i in range(len(keys)):
		outputFile.write('     {\n')
		outputFile.write('           "key" : "{0}" , \n'.format(keys[i]))
		outputFile.write('           "values": {0}\n'.format(myDict[keys[i]]))
		outputFile.write('     }')
		if i < (len(keys) - 1): outputFile.write(',\n')
	outputFile.write('\n]\n')


	inputFile.close()
	outputFile.close()

except IOError:
	print 'Error: No such file'
