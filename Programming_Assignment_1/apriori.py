# -*- coding: utf-8 -*- 
import sys

# open files
def fileOpen(fileName, mode):
	try:
		file = open(fileName, mode)
		return file
	except FileNotFoundError as e:
		print('There is no file with name', fileName)
		sys.exit(1)

# make frequent pattern list
'''
output example
[
	{1}, {2}, {3}, {1,2}, {2,3}, {1,3}, {1,2,3}
]
'''
def makeFreqPatternList(transactionList, supportDict):
	print('\n* making frequent pattern list ...')
	freqPatternList = []
	subsetDict = makeLengthOneSubsetsDict(transactionList)
	freqPatternDict = findFreqPatternDict(subsetDict, [])
	subsetList = freqPatternDict.keys()
	supportDict.update(freqPatternDict)

	for item in subsetList:
		freqPatternList.append(item)

	supersetList = []
	supersetDict = {}
	freqPatternDict = {}

	for length in range(2, getMaximumLength(transactionList)):
		if len(subsetList) < 1:
			break

		supersetList = makeSupersetList(subsetList, length)
		supersetDict = makeSupersetDict(transactionList, supersetList)
		freqPatternDict = findFreqPatternDict(supersetDict, subsetList)
		supportDict.update(freqPatternDict)

		for item in freqPatternDict.keys():
			freqPatternList.append(item)

		subsetList = freqPatternDict.keys()

	print('* complete making frequent pattern list')
	return freqPatternList

# make length-1 subsets dict
def makeLengthOneSubsetsDict(wholeList):
	freqItemDict = {}
	for line in wholeList:
		for item in line:
			numList = []
			numList.append(int(item))
			itemset = frozenset(numList)
			if itemset in freqItemDict:
				freqItemDict[itemset] += 1
			else:
				freqItemDict[itemset] = 1

	return freqItemDict

# find frequent pattern
# remove itemset that has support less than minimum support
def findFreqPatternDict(inputDict, subsetList):
	freqPatternDict = {}

	for key in inputDict:
		if (inputDict[key] / float(transactionNum) * 100) >= minimumSupport:
			if len(key) > 1 and not(checkIfAllSubsetIsFreq(key, subsetList)):
				continue
			freqPatternDict[key] = inputDict[key]

	return freqPatternDict

# pruning
# check if all subset(has length k-1) is frequent
'''
When we check whether a itemset {a, b, c} is frequent,					(length : 3)
we have to check if the itemsets {a,b}, {b,c}, and {a,c} are frequent.	(length : 2)
'''
def checkIfAllSubsetIsFreq(superset, subsetList):
	cnt = 0
	supersetLen = len(superset)
	for item in subsetList:
		if cnt == supersetLen:
			return True
		if item.issubset(superset):
			cnt += 1

	if cnt == supersetLen:
		return True
	else:
		return False

#get maximum length of transaction in transaction list
def getMaximumLength(transactionList):
	maxLen = 0
	for item in transactionList:
		if len(item) > maxLen:
			maxLen = len(item)

	print('maximum length in the transactions : ' + str(maxLen))
	return maxLen

# make superset length+1
'''
If we have {a,b}, {b,c}, {c,a} ... frequent items, 				(length : 2)
we can make {a,b,c} = {a,b} U {b,c} for another frequent item.	(length : 3)
'''
def makeSupersetList(setList, length):
	supersetList = []

	maxIdx = len(setList)

	for i in range(0, maxIdx):
		for j in range(i, maxIdx):
			if i==j:
				continue
			interSet = set(setList[i]).union(set(setList[j]))
			if len(interSet) != length:
				continue
			if interSet not in supersetList:
				supersetList.append(interSet)

	return supersetList

# make superset dict
'''
output example
{
	{1,2,3} : 10
	{3,4} : 3
	{5,6,7} : 5
	...
}
'''
def makeSupersetDict(transactionList, supersetList):
	supersetDict = {}
	for transaction in transactionList:
		for superset in supersetList:
			if(superset.issubset(transaction)):
				superset = frozenset(superset)
				if superset in supersetDict:
					supersetDict[superset] += 1
				else:
					supersetDict[superset] = 1

	return supersetDict

# remove length one frequent pattern
# When we make association rules, we make it with subsets of frequent patterns.
# So, if a frequent pattern's length is one, its subset is just an empty set.
# Therefore, that frequent pattern can't make association rule.
# That's why we have to remove length one frequent pattern.
def removeLengthOneFreqPattern(freqPatternList):
	changedList = []
	for item in freqPatternList:
		if len(item) > 1:
			changedList.append(item)

	return changedList


# make association rules
# make association rules by using all frequent itemsets 
def makeAssociationRules(transactionList, transactionNum, freqPatternList, fWrite, supportDict):
	print('\n* making association rules...')
	maxIdx = len(freqPatternList)

	cnt = 0

	for i in range(0, maxIdx):
		supportNum = supportDict[freqPatternList[i]]
		support = round(supportNum / float(transactionNum) * 100, 2)
		subsetList = makeSubsetsForAssociationRules(freqPatternList[i])

		print("\nassociation rule for " + makeFormattedSet(freqPatternList[i]))

		for j in range(0, len(subsetList)):
			confidenceDino = supportDict[frozenset(subsetList[j][0])]
			confidence = round(supportNum/ float(confidenceDino) * 100, 2)

			print(makeFormattedSet(subsetList[j][0])
				+ '\t'
				+ makeFormattedSet(subsetList[j][1])
				+ '\t'
				+ str('%.2f'%support)
				+ '\t'
				+ str('%.2f'%confidence))

			fWrite.write(makeFormattedSet(subsetList[j][0]) 
				+ '\t'
				+ makeFormattedSet(subsetList[j][1])
				+ '\t'
				+ str('%.2f'%support)
				+ '\t'
				+ str('%.2f'%confidence)
				+ '\n')
			cnt += 1

	print('\nThere are ' + str(cnt) + ' association rules.')

# make subsets for association rules
# if we have {1,2,3,4} for frequnet pattern,
# it will give you like this data:
'''
setOfRules = [
	[{1}, {2,3,4}],
	[{2}, {1,3,4}],
	[{3}, {1,2,4}],
	...
	, [{2,3,4}, {1}]
]

this data is for getting association rules like this :
{1} -> {2,3,4}
{2} -> {1,3,4}
...
{2,3,4} -> {1}
'''
def makeSubsetsForAssociationRules(freqPattern):
	patternLen = len(freqPattern)
	setOfRules = []

	for i in range(1, patternLen):
		itemSets = map(set, list(combinations(freqPattern, i)))
		associItemSets = []

		for j in range(0, len(itemSets)):
			associSet = freqPattern - itemSets[j]
			itemInRules = []
			itemInRules.append(itemSets[j])
			itemInRules.append(associSet)

			setOfRules.append(itemInRules)

	return setOfRules

# make combinations in frequent patterns
def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = range(r)
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)

# make formatted set
# to make 'set format' string
# ex) set([1,2,3]) -> {1,2,3}
def makeFormattedSet(inputSet):
	formattedSetList = []
	formattedSetList.append('{')

	for item in inputSet:
		formattedSetList.append(str(item))
		formattedSetList.append(',')

	del formattedSetList[-1]
	formattedSetList.append('}')

	return ''.join(formattedSetList)


if __name__ == '__main__':
	# check if user inserted 4 arguments
	if len(sys.argv) != 4:
		print('\n* How to execute : ')
		print('apriori.exe [minimumSupport] [input_file] [output_file]\n')
		sys.exit(1)

	# get minimum support, input file name, and output file name from input
	try:
		minimumSupport = int(sys.argv[1])
		print 'Minimum Support : ' + str(minimumSupport) + '%'
	except ValueError as e:
		print('\n* How to execute : ')
		print('apriori.exe [minimumSupport] [input_file] [output_file]\n')
		print('You have to insert integer for the minimum support\n')
		sys.exit(1)

	inputFileName = sys.argv[2]
	outputFileName = sys.argv[3]
	

	# open files
	f = fileOpen(inputFileName, 'r')
	fWrite = fileOpen(outputFileName, 'w')

	# transaction list initialize
	transactionList = []

	# read line from input data file
	# list of sets
	while True:
	    line = f.readline()
	    if not line: break

	    itemSet = line.split()
	    itemSet = map(int, itemSet)

	    transactionList.append(set(itemSet))

	# get the number of transactions
	transactionNum = len(transactionList)
	print("the number of transaction sets : " + str(transactionNum))

	# support dict for frequent patterns
	supportDict = {}

	# get the list of the frequent items
	freqPatternList = makeFreqPatternList(transactionList, supportDict)

	#remove length 1 frequent patterns
	freqPatternList = removeLengthOneFreqPattern(freqPatternList)

	# make association rules with the list of the frequent items
	makeAssociationRules(transactionList, transactionNum, freqPatternList, fWrite, supportDict)

	#close files
	f.close()
	fWrite.close()

































