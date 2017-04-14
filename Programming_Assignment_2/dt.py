# -*- coding: utf-8 -*- 
import sys				#arvg, exit
import collections		#orderedDict
import math 			#log
import pygraphviz as pg

# class for decision tree
class DecisionTree():
	def __init__(self, key, value):
		self.key = key
		self.value = value
		self.children = []
		self.tuples = []
		self.attributesRemained = []
		self.label = 'unlabeled'

# open files
def fileOpen(fileName, mode):
	try:
		file = open(fileName, mode)
		return file
	except FileNotFoundError as e:
		print('There is no file with name', fileName)
		sys.exit(1)

def getAttributes(trainingFile):
	attributeLine = trainingFile.readline()
	attributes = attributeLine.split()

	return attributes

def makeTupleList(trainingFile, attributes):
	tupleList = []

	while True:
		line = trainingFile.readline()

		if not line: break

		itemValues = line.split()
		tupleDict = collections.OrderedDict()

		for idx in range(0,len(attributes)):
			tupleDict[attributes[idx]] = itemValues[idx]
		tupleList.append(tupleDict)

	return tupleList

def expandDecisionTree(node, method, classLabel, classLabelValueList = []):
	if len(node.attributesRemained) == 1:
		node.label = getPossibleLabelByVoting(node.tuples, classLabel)
		return

	label = getPossibleLabel(node.tuples, classLabel)
	if label != '':
		node.label = label
		return

	isRoot = False
	if node.key == 'root':
		isRoot = True

	attributeDict = collections.OrderedDict()
	#make attributes dict
	attributeDict = makeAttributeDict(node.tuples, node.attributesRemained, classLabel, classLabelValueList,isRoot)

	# make attribute value dict
	valueDict = collections.OrderedDict()
	valueDict = makeValueDict(valueDict, node.tuples, attributeDict, classLabel, node.attributesRemained)

	# count num of tuples for getting information gain
	valueDict = countTupleNumForInfoGain(node.tuples, valueDict, classLabel, node.attributesRemained)

	# calculate information gain
	scoreDict = collections.OrderedDict()
	totalInfoDict = collections.OrderedDict()
	totalInfoDict = calTotalInfo(valueDict, len(node.tuples), classLabel, classLabelValueList)
	infoDict = collections.OrderedDict()
	infoDict = calInfoDict(valueDict, len(node.tuples))
	infoGainDict = calInfoGain(totalInfoDict, infoDict)
	if method == 'infoGain':
		scoreDict = infoGainDict
	elif method == 'gainRatio':
		scoreDict = collections.OrderedDict()
		scoreDict = calGainRatio(valueDict, infoGainDict, len(node.tuples), classLabel, classLabelValueList)

	# find attribute for decision by information gain dictionary
	attributeForDecision = findAttributeForDecision(scoreDict, method)
	if attributeForDecision == '':
		return

	# make children node
	childrenNodeDict = {}

	for item in attributeDict[attributeForDecision]:
		childrenNodeDict[item] = DecisionTree(attributeForDecision, item)
		for attribute in node.attributesRemained:
			if attribute != attributeForDecision:
				childrenNodeDict[item].attributesRemained.append(attribute)
	
	for item in node.tuples:
		childrenNodeDict[item[attributeForDecision]].tuples.append(item)

	for key, value in childrenNodeDict.items():
		if len(value.tuples) != 0:
			node.children.append(value)

	for item in node.children:
		expandDecisionTree(item, method, classLabel, classLabelValueList)

def makeAttributeDict(tupleList, attributesRemained, classLabel, classLabelValueList, isRoot = False):
	attributeDict = collections.OrderedDict()

	for tupleItem in tupleList:
		for key, value in tupleItem.items():
			if key == classLabel and isRoot == True:
				if classLabel not in attributeDict:
					attributeDict[classLabel] = []
				if value not in attributeDict[classLabel]:
					attributeDict[classLabel].append(value)
				if value not in classLabelValueList:
					classLabelValueList.append(value)
			if key not in attributesRemained:
				continue
			if key not in attributeDict.keys():
				attributeList = []
				attributeList.append(value)
				attributeDict[key] = attributeList
			else:
				if value not in attributeDict[key]:
					attributeDict[key].append(value)

	attributeDict[classLabel] = classLabelValueList

	return attributeDict

def makeValueDict(valueDict, tupleList, attributeDict, classLabel, attributes):
	classLabelValues = attributeDict[classLabel]

	tempDict = collections.OrderedDict()

	for key, value in attributeDict.items():
		if key == classLabel:
			continue

		subDict = collections.OrderedDict()

		for item in value:
			leafDict = collections.OrderedDict()

			for idx in range(0, len(classLabelValues)):
				leafDict[classLabelValues[idx]] = 0
			subDict[item] = leafDict

		valueDict[key] = subDict

	return valueDict

def countTupleNumForInfoGain(tupleList, valueDict, classLabel, attributes):
	for tupleItem in tupleList:
		classLabelValue = tupleItem[classLabel]
		for key, value in tupleItem.items():
			if key == classLabel or key not in attributes:
				continue

			valueDict[key][value][classLabelValue] += 1

	return valueDict

def calInfoDict(valueDict, numOfTuples):
	infoDict = collections.OrderedDict()

	for key, value in valueDict.items():
		infoValue = 0

		for key2, value2 in value.items():
			countedValuesOfOneCate = value2.values()
			infoValue += calItemOfInfoGain(numOfTuples, countedValuesOfOneCate)

		infoDict[key] = infoValue

	return infoDict			

def calItemOfInfoGain(numOfTuples, countedValuesOfOneCate):
	sumOfValues = getSumOfValues(countedValuesOfOneCate)

	sumOfExpInfo = 0
	for item in countedValuesOfOneCate:
		sumOfExpInfo += calExpInfo(item, sumOfValues)

	return sumOfValues/float(numOfTuples) * sumOfExpInfo

def getSumOfValues(countedValues):
	result = 0

	for item in countedValues:
		result += item

	return result

def calExpInfo(nume,dino):
	if(nume == 0):
		return 0
	return -(nume/float(dino) * math.log((nume/float(dino)),2))

def calTotalInfo(valueDict, numOfTuples, classLabel, classLabelValueList):
	totalInfoDict = collections.OrderedDict()

	for key, value in valueDict.items():
		totalInfoValue = 0

		for classLabelValue in classLabelValueList:
			sectorSum = 0

			for key2, value2 in value.items():
				sectorSum += value2[classLabelValue]

			totalInfoValue += calExpInfo(sectorSum, numOfTuples)

		totalInfoDict[key] = totalInfoValue

	return totalInfoDict

def calInfoGain(totalInfoDict, infoDict):
	infoGainDict = collections.OrderedDict()

	for key, value in totalInfoDict.items():
		infoGainDict[key] = totalInfoDict[key] - infoDict[key]

	return infoGainDict

def calGainRatio(valueDict, totalInfoDict, numOfTuples, classLabel, classLabelValueList):
	gainRatioDict = collections.OrderedDict()

	for key, value in valueDict.items():
		split = 0
		for key2, value2 in value.items():
			ratioItem = 0
			for classLabel in classLabelValueList:
				ratioItem += value2[classLabel]
			#print(key, 'ratioItem : ' , ratioItem)
			#print('num of tuples : ' , str(numOfTuples))
			split += calExpInfo(ratioItem, numOfTuples)
			#print('split item', calExpInfo(ratioItem, numOfTuples))
		#print(key, ' split : ', split)
		#print('totalInfo : ', totalInfoDict[key])
		#print('gainRatio : ', totalInfoDict[key]/split)

		gainRatioDict[key] = totalInfoDict[key] / split

	return gainRatioDict

def findAttributeForDecision(scoreDict, method):
	attributeForDecision = ''

	if method == 'infoGain' or method == 'gainRatio':
		maxInfoGain = 0

		for key, value in scoreDict.items():
			if value > maxInfoGain:
				maxInfoGain = value
				attributeForDecision = key


	return attributeForDecision

def getPossibleLabel(tuples, classLabel):
	firstValue = tuples[0][classLabel]

	for idx in range(1, len(tuples)):
		if tuples[idx][classLabel] != firstValue:
			return ''

	return firstValue

def getPossibleLabelByVoting(tuples, classLabel):
	labelDict = {}
	for item in tuples:
		if item[classLabel] not in labelDict:
			labelDict[item[classLabel]] = 1
		else:
			labelDict[item[classLabel]] += 1

	maxNum = 0
	possibleLabel = ''
	for key, value in labelDict.items():
		if value > maxNum:
			maxNum = value
			possibleLabel = key

	return possibleLabel

def printDict(inputDict):
	for key, value in inputDict.items():
		print(key, value)

def printDecisionTree(node, treeFile):
	
	print('node key : ' + node.key)
	print('node value : ' + str(node.value))
	print('node tuples : ')
	treeFile.write('node key : ' + node.key + '\n')
	treeFile.write('node value : ' + str(node.value) + '\n')
	treeFile.write('node tuples # : ' + str(len(node.tuples)) + '\n')

	for item in node.tuples:
		print(item)
		#treeFile.write(item)

	print('remained attributes : ' + str(node.attributesRemained))
	print('node label : ' + node.label)
	print('\n\n')

	treeFile.write('remained attributes : ' + str(node.attributesRemained) + '\n')
	treeFile.write('node label : ' + node.label + '\n')
	treeFile.write('\n\n')

	for child in node.children:
		printDecisionTree(child, treeFile)

def classifyTestData(testFile, outputFile, rootNode, attributes, classLabel):
	attributeStr = '\t'.join(attributes)
	outputFile.write(attributeStr+'\n')

	testFile.readline()

	testTupleList = []

	while True:
		line = testFile.readline()

		if not line: break

		itemValues = line.split()
		tupleDict = collections.OrderedDict()

		for idx in range(0,len(attributes)):
			if attributes[idx] == classLabel:
				continue
			tupleDict[attributes[idx]] = itemValues[idx]
		testTupleList.append(tupleDict)

	for item in testTupleList:
		findLabel(item, rootNode, classLabel)

		valueStr = '\t'.join(item.values())
		outputFile.write(valueStr+'\n')

def findLabel(tupleItem, node, classLabel):
	if node.label != 'unlabeled':
		tupleItem[classLabel] = node.label
	else:
		childrenValues = []
		for child in node.children:
			childrenValues.append(child.value)

		if tupleItem[node.children[0].key] in childrenValues:
			for child in node.children:
				if child.value == tupleItem[child.key]:
					findLabel(tupleItem, child, classLabel)
		else:
			maxNum = 0
			maxLabel = ''

			for child in node.children:
				if len(child.tuples) > maxNum:
					maxNum = len(child.tuples)
					maxLabel = child.value

			for child in node.children:
				if child.value == maxLabel:
					findLabel(tupleItem, child, classLabel)

def makeGraph(node, graph):
    #parentStr = node.key + ' ' + str(node.value) + ' ' + node.label + ' ' + str(len(node.tuples))
    parentStr = str(len(node.tuples)) + '.' + node.key + ':' + str(node.value)
    for child in node.children:
        #childStr = child.key + ' ' + child.value + ' ' + child.label + ' ' + str(len(child.tuples))
        childStr = str(len(child.tuples)) + '.' + child.key + ':' + child.value
        graph.add_edge(parentStr, childStr)
        makeGraph(child,graph)

def drawGraph(graph):
	graph.layout(prog='dot')
    
	graph.draw('file.png')
    
	graph.graph_attr.update(size="2,12")
	graph.graph_attr.update(ratio="compress")


if __name__ == '__main__':
	# check if user inserted 4 arguments
	if len(sys.argv) != 4:
		print('\n* How to execute : ')
		print('python dt.py [training_file] [test_file] [output_file]\n')
		sys.exit(1)

	# get the file names for the arguments
	trainingFileName = sys.argv[1]
	testFileName = sys.argv[2]
	outputFileName = sys.argv[3]

	# open file
	trainingFile = fileOpen(trainingFileName, 'r')
	testFile = fileOpen(testFileName, 'r')
	outputFile = fileOpen(outputFileName, 'w')

	# get attributes from the training file
	attributes = getAttributes(trainingFile)

	# make list of tuples from the training file
	tupleList = makeTupleList(trainingFile, attributes)

	# separate class label from other attributes
	classLabel = attributes[-1]

	rootNode = DecisionTree("root",0)
	rootNode.tuples = tupleList
	rootNode.attributesRemained = attributes

	expandDecisionTree(rootNode, "gainRatio", classLabel)

	treeFile = open("tree.txt", "w")
	printDecisionTree(rootNode, treeFile)

	classifyTestData(testFile, outputFile, rootNode, attributes, classLabel)

	#graph = pg.AGraph(directed=True, strict=True)

	#makeGraph(rootNode, graph)

	#drawGraph(graph)
	






