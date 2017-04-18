# -*- coding: utf-8 -*- 
import sys				#arvg, exit
import collections		#orderedDict
import math 			#log

# class for decision tree
class DecisionTree():
	'''
	key : attribute
	value : attribute value
	children : children nodes
	tuples : data tuple in node
	attributesRemained : attributes that are not used for classification yet
	label : If the node is leaf, it has label. If not, it is 'unlabeled'
	'''
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

# first line of training file is the list of attributes
# we can get attributes here
def getAttributes(trainingFile):
	attributeLine = trainingFile.readline()
	attributes = attributeLine.split()

	return attributes

# read data tuples, and make list of the tuples
# tuple will be saved in dictionary form
'''
[
	{"age" : "<=30", "income" : "high", ...},
	{"age" : "40", ...}, 
	...
]
'''
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

# expanding the decision tree
def expandDecisionTree(node, method, classLabel, classLabelValueList = []):
	# if this node has the class label for attributesRemained, this node can't expand children.
	# so we have to label this node by voting.
	if len(node.attributesRemained) == 1:
		node.label = getPossibleLabelByVoting(node.tuples, classLabel)
		return

	# decide whether this node can be labeled or not.
	# if every tuples in this node have the same class label value, this node can be labeled.
	label = getPossibleLabel(node.tuples, classLabel)
	if label != '':
		node.label = label
		return

	# root node need to be marked for getting class label values.	
	isRoot = False
	if node.key == 'root':
		isRoot = True

	# make attributes dict
	attributeDict = collections.OrderedDict()
	attributeDict = makeAttributeDict(node.tuples, node.attributesRemained, classLabel, classLabelValueList, isRoot)

	# make attribute value dict
	valueDict = collections.OrderedDict()
	valueDict = makeValueDict(valueDict, node.tuples, attributeDict, classLabel, node.attributesRemained)

	# count num of tuples for getting information gain
	valueDict = countTupleNumForInfoGain(node.tuples, valueDict, classLabel, node.attributesRemained)

	# calculate score dictionary for information gain, gain ratio, or gini index
	scoreDict = collections.OrderedDict()
	totalInfoDict = collections.OrderedDict()
	infoDict = collections.OrderedDict()
	totalInfoDict = calTotalInfo(valueDict, len(node.tuples), classLabel, classLabelValueList)
	infoDict = calInfoDict(valueDict, len(node.tuples))
	infoGainDict = calInfoGain(totalInfoDict, infoDict)

	if method == 'infoGain':
		scoreDict = infoGainDict
	elif method == 'gainRatio':
		scoreDict = calGainRatio(valueDict, infoGainDict, len(node.tuples), classLabel, classLabelValueList)
	elif method == 'giniIndex':
		scoreDict = calGiniIndex(valueDict, len(node.tuples), classLabel, classLabelValueList)

	# find attribute for decision by score dictionary
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

	# expand the decision tree recursively
	for item in node.children:
		expandDecisionTree(item, method, classLabel, classLabelValueList)

# making attribute dictionary
# outputs like this : 
'''
attributeDictionary
{
	"age" : ["<=30", "31...40", ">40"],
	"income" : ["high", "med", "low"],
	...
}

classLabelValueList
["yes", "no"]
'''
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

# making value dictionary for counting
'''
output like this : 
{
	"age" : {
		"<=30" : {
			"yes" : 0,
			"no" : 0
		},
		"31...40" : {
			"yes" : 0,
			"no" : 0
		}, ...
	},
	"income" : {
		...
	}
	...
}
'''
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

# this process is exactly fill the blanks of valueDict by counting
'''
output like this : 
{
	"age" : {
		"<=30" : {
			"yes" : 2,
			"no" : 3
		},
		"31...40" : {
			"yes" : 4,
			"no" : 0
		}, ...
	},
	"income" : {
		...
	}
	...
}
'''
def countTupleNumForInfoGain(tupleList, valueDict, classLabel, attributes):
	for tupleItem in tupleList:
		classLabelValue = tupleItem[classLabel]
		for key, value in tupleItem.items():
			if key == classLabel or key not in attributes:
				continue

			valueDict[key][value][classLabelValue] += 1

	return valueDict

# calculate expected information of each attributes
def calInfoDict(valueDict, numOfTuples):
	infoDict = collections.OrderedDict()

	for key, value in valueDict.items():
		infoValue = 0

		for key2, value2 in value.items():
			countedValuesOfOneCate = value2.values()
			infoValue += calItemOfInfoGain(numOfTuples, countedValuesOfOneCate)

		infoDict[key] = infoValue

	return infoDict			

# calculate expected information item of each attribute values
def calItemOfInfoGain(numOfTuples, countedValuesOfOneCate):
	sumOfValues = getSumOfValues(countedValuesOfOneCate)

	sumOfExpInfo = 0
	for item in countedValuesOfOneCate:
		sumOfExpInfo += calExpInfo(item, sumOfValues)

	return sumOfValues/float(numOfTuples) * sumOfExpInfo

# get sum of tuples that have certain attribute value
def getSumOfValues(countedValues):
	result = 0

	for item in countedValues:
		result += item

	return result

# calculate expected information
def calExpInfo(nume,dino):
	if(nume == 0):
		return 0
	return -(nume/float(dino) * math.log((nume/float(dino)),2))

# calculate total expected information of attribute
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

# calculate information gain
def calInfoGain(totalInfoDict, infoDict):
	infoGainDict = collections.OrderedDict()

	for key, value in totalInfoDict.items():
		infoGainDict[key] = totalInfoDict[key] - infoDict[key]

	return infoGainDict

# calculate gain ratio
def calGainRatio(valueDict, totalInfoDict, numOfTuples, classLabel, classLabelValueList):
	gainRatioDict = collections.OrderedDict()

	for key, value in valueDict.items():
		split = 0
		for key2, value2 in value.items():
			ratioItem = 0
			for classLabel in classLabelValueList:
				ratioItem += value2[classLabel]
			split += calExpInfo(ratioItem, numOfTuples)

		gainRatioDict[key] = totalInfoDict[key] / split

	return gainRatioDict

# calculate gini index
def calGiniIndex(valueDict, numOfTuples, classLabel, classLabelValueList):
	giniDict = collections.OrderedDict()

	for key, value in valueDict.items():
		candidateForGini = []
		for key2, value2 in value.items():
			hasKey = 0
			hasKeyDict = collections.OrderedDict()
			notHasKey = 0
			notHasKeyDict = collections.OrderedDict()
			for key3, value3 in value.items():
				if key2 == key3:
					for classLabel in classLabelValueList:
						hasKey += value3[classLabel]
						if classLabel in hasKeyDict:
							hasKeyDict[classLabel] += value3[classLabel]
						else:
							hasKeyDict[classLabel] = value3[classLabel]
				else:
					for classLabel in classLabelValueList:
						notHasKey += value3[classLabel]
						if classLabel in notHasKeyDict:
							notHasKeyDict[classLabel] += value3[classLabel]
						else:
							notHasKeyDict[classLabel] = value3[classLabel]

			hasKeyValue = calGiniIndexItem(hasKey, numOfTuples, hasKeyDict)
			notHasKeyValue = calGiniIndexItem(notHasKey, numOfTuples, notHasKeyDict)

			candidateForGini.append(hasKeyValue + notHasKeyValue)

		giniDict[key] = min(candidateForGini)

	return giniDict

# calculate gini index item
def calGiniIndexItem(numOfHasKey, numOfTuples, hasKeyDict):
	sumOfClassLabelItem = 0
	for key, value in hasKeyDict.items():
		sumOfClassLabelItem += (value / float(numOfHasKey)) * (value / float(numOfHasKey))

	return numOfHasKey / float(numOfTuples) * (1-sumOfClassLabelItem)

# With score dictionary, we have to find attribute for certain step
def findAttributeForDecision(scoreDict, method):
	attributeForDecision = ''

	if method == 'infoGain' or method == 'gainRatio':
		attributeForDecision = max(scoreDict, key=scoreDict.get)
	elif method == 'giniIndex':
		attributeForDecision = min(scoreDict, key=scoreDict.get)

	return attributeForDecision

# decide whether this node can be labeled or not.
# if every tuples in this node have the same class label value, this node can be labeled.
def getPossibleLabel(tuples, classLabel):
	firstValue = tuples[0][classLabel]

	for idx in range(1, len(tuples)):
		if tuples[idx][classLabel] != firstValue:
			return ''

	return firstValue

# if this node has the class label for attributesRemained, this node can't expand children.
# so we have to label this node by voting.
def getPossibleLabelByVoting(tuples, classLabel):
	labelDict = {}
	for item in tuples:
		if item[classLabel] not in labelDict:
			labelDict[item[classLabel]] = 1
		else:
			labelDict[item[classLabel]] += 1

	possibleLabel = max(labelDict, key=labelDict.get)

	return possibleLabel

# read test file
# input each tuple into the decision tree, and find the label
# after finding the label, write the tuple with label into output file
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

# from the root node, find the label along the decision tree recursively
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

	# open files
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

	classifyTestData(testFile, outputFile, rootNode, attributes, classLabel)

	# close files
	trainingFile.close()
	testFile.close()
	outputFile.close()





