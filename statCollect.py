import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('config_path', help = "path of 'config.json'")
args = parser.parse_args()

try:
	config = json.loads(open(args.config_path, 'r').read())
except:
	print 'Error: No such config.json file'

LOG_FILE_BASE = config['log_file_base']
LOG_PRECISION = config['log_precision']

RCV_LOG_FILE = LOG_FILE_BASE + 'rcv.log'
RCV_JSON_FILE = LOG_FILE_BASE + 'rcv.json'
SND_LOG_FILE = LOG_FILE_BASE + 'snd.log'
SND_JSON_FILE = LOG_FILE_BASE + 'snd.json'
GNL_LOG_FILE = LOG_FILE_BASE + 'gnl.json'	# general information
OUT_FILE_PATH = LOG_FILE_BASE + 'stat.json'

def ff(timestamp):
	if LOG_PRECISION:
		return float('%{0}f'.format(LOG_PRECISION) % float(timestamp))
	else:
		return int(float(timestamp))	

def readLogFile(in_path, out_path, mode = 'a+'):
	inputFile = open(in_path, 'r')
	outputFile = open(out_path, mode)
	myDict = dict()		

	# Determine the start and end time
	line = inputFile.readline()
	line = inputFile.readline().split(';')
	start_time = ff(line[1])
	end_time = None
	step_size = ff(LOG_PRECISION)

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

	# Initialize each list
	for key in myDict.keys():
		myDict[key] = list()
		myDict[key] = [0] * (step_count + 1)

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
	

def readJsonFile(in_path):
	inputFile = open(in_path, 'r')
	myDict = json.loads(inputFile.read())
	return myDict


stat = dict()
outputFile = open(OUT_FILE_PATH, 'w+')

readLogFile(SND_LOG_FILE, SND_JSON_FILE, 'w+')
stat['snd_info'] = json.loads(open(SND_JSON_FILE, 'r').read())

readLogFile(RCV_LOG_FILE, RCV_JSON_FILE, 'w+')
stat['rcv_info'] = json.loads(open(RCV_JSON_FILE, 'r').read())

stat['general_info'] = readJsonFile(GNL_LOG_FILE)

outputFile.write(json.dumps(stat))
outputFile.close()