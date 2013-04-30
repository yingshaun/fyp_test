import argparse
parser = argparse.ArgumentParser()
parser.add_argument("inputFile", help = "relative path of the log file")
parser.add_argument('-o', '--output', help = 'output json file (default: converted_log_file.json)')
parser.add_argument('-p', '--precision', help = 'precision of timestamp (e.g. 0 (int), 0.1, 0.01)')
args = parser.parse_args()

def ff(timestamp):
	if args.precision:
		return float('%{0}f'.format(args.precision) % float(timestamp))
	else:
		return int(float(timestamp))	

# Open the input log file
try:
	inputFile = open(args.inputFile, 'r')
	if args.output:
		outputFile = open(args.output, 'w+')
	else:
		outputFile = open('converted_log_file.json', 'w+')

	myDict = dict()	

	# Determine the start and end time
	line = inputFile.readline()
	line = inputFile.readline().split(';')
	start_time = ff(line[1])
	end_time = None
	step_size = ff(args.precision)

	inputFile.seek(0, 0)
	while True:
                line = inputFile.readline()
                if line == '': break            # EOF
                elif line[0] == '#': continue   # Comment
                else:
                        line = line.split(';')
			if ff(line[1]) > end_time: end_time = ff(line[1])
			if myDict.get(line[0]) == None:
				myDict[line[0]] = True
	step_count = int((end_time - start_time) / step_size) + 1

	print 'Start time: ' + str(start_time)
	print 'End time: ' + str(end_time)
	print 'Step size: ' + str(step_size)
	print 'Step Count: ' + str(step_count)
	print myDict

	# Initialize each list
	for key in myDict.keys():
		myDict[key] = list()
		myDict[key] = [0] * step_count


	# Read each value
	inputFile.seek(0, 0)
	while True:
		line = inputFile.readline()
		if line == '': break		# EOF
		elif line[0] == '#': continue	# Comment
		else:
			line = line.split(';')
			index = int(ff((float(line[1]) - start_time) / step_size))
			print float(line[1]), ff((float(line[1]) - start_time)/step_size), index, int(line[2])
			myDict[line[0]][index] = int(line[2])

	print myDict
	
	outputFile.write('[\n')
	keys = myDict.keys()
	for i in range(len(keys)):
		outputFile.write('     {\n')
		outputFile.write('           "key" : "{0}" , \n'.format('(' + keys[i][2:]))
		outputFile.write('           "values": [')
		myList = myDict[keys[i]]
		for j in range(len(myList) - 1):
			outputFile.write('[{0}, {1}], '.format(ff(j * step_size), myList[j]))
		j = len(myList) - 1
		outputFile.write('[{0}, {1}]'.format( ff(j * step_size) , myList[j]))

		outputFile.write(']\n')
		outputFile.write('     }')
		if i < (len(keys) - 1): outputFile.write(',\n')
	outputFile.write('\n]\n')


	inputFile.close()
	outputFile.close()

except IOError:
	print 'Error: No such file'
