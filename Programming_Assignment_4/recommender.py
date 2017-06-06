# -*- coding: utf-8 -*-
import sys 				#arvg, exit
import collections		#orderedDict
import math 			#sqrt
import datetime 		#now


class RatingTuple():
	def __init__(self, userId, itemId, rating, timeStamp):
		self.userId = userId
		self.itemId = itemId
		self.rating = rating
		self.timeStamp = timeStamp

class RatingMatrixCell():
	def __init__(self, rating, timeStamp):
		self.rating = rating
		self.timeStamp = timeStamp

# open files
def fileOpen(fileName, mode):
	try:
		file = open(fileName, mode)
		return file
	except FileNotFoundError as e:
		print('There is no file with name', fileName)
		sys.exit(1)

def getDataFromFile(file):
	dataTuples = []

	while True:
		line = file.readline()

		if not line: break

		values = line.split()

		ratingTupleNode = RatingTuple(int(values[0]), int(values[1]), int(values[2]), int(values[3]))

		dataTuples.append(ratingTupleNode)

	return dataTuples

def assignRatingMatrix(ratingMatrixDict, trainingDataTuples):
	for item in trainingDataTuples:
		if item.userId not in ratingMatrixDict:
			ratingMatrixDict[item.userId] = collections.OrderedDict()
		ratingMatrixDict[item.userId][item.itemId] = RatingMatrixCell(item.rating, item.timeStamp)

def calPcc(ratingMatrixDict):
	pccDict = collections.OrderedDict()
	'''
	for key, value in ratingMatrixDict.items():
		for key2, value2 in ratingMatrixDict.items():
			if key>=key2:
				continue

			set1 = set(value.keys())
			set2 = set(value2.keys())
			commonItemList = list(set1.intersection(set2))

			if(len(commonItemList) == 0):
				continue

			ratingAvgDict = calRatingAvg(ratingMatrixDict, key, key2, commonItemList)

			pccValue = _calPcc(ratingMatrixDict, key, key2,commonItemList, ratingAvgDict)

			if key not in pccDict:
				pccDict[key] = collections.OrderedDict()

			if key2 not in pccDict:
				pccDict[key2] = collections.OrderedDict()

			pccDict[key][key2] = pccValue
			pccDict[key2][key] = pccValue
	'''

	maximumIdx = len(ratingMatrixDict.keys())
	for idx in range(0, maximumIdx):
		#print(str(idx) + " : idx")
		if idx % 10 == 0:
			print(str(idx) + " / " + str(maximumIdx) + " calculating PCC")
		for idx2 in range(idx+1, maximumIdx):
			#if idx2 % 450 == 0:
			#	print(str(idx2) + " : small idx")
			key1 = ratingMatrixDict.keys()[idx]
			key2 = ratingMatrixDict.keys()[idx2]

			set1 = set(ratingMatrixDict[key1].keys())
			set2 = set(ratingMatrixDict[key2].keys())
			commonItemList = list(set1.intersection(set2))

			if(len(commonItemList) == 0):
				continue

			ratingAvgDict = calRatingAvg(ratingMatrixDict, key1, key2, commonItemList)

			pccValue = _calPcc(ratingMatrixDict, key1, key2 ,commonItemList, ratingAvgDict)

			if key1 not in pccDict:
				pccDict[key1] = collections.OrderedDict()

			if key2 not in pccDict:
				pccDict[key2] = collections.OrderedDict()

			pccDict[key1][key2] = pccValue
			pccDict[key2][key1] = pccValue

	return pccDict


def calRatingAvg(ratingMatrixDict, userId1, userId2, commonItemList):
	ratingSum1 = 0
	ratingSum2 = 0
	
	for item in commonItemList:
		ratingSum1 += ratingMatrixDict[userId1][item].rating
		ratingSum2 += ratingMatrixDict[userId2][item].rating
	

	'''
	for key, value in ratingMatrixDict[userId1].items():
		ratingSum1 += value.rating

	for key, value in ratingMatrixDict[userId2].items():
		ratingSum2 += value.rating
	'''

	
	ratingAvg1 = ratingSum1 / float(len(commonItemList))
	ratingAvg2 = ratingSum2 / float(len(commonItemList))
	

	'''
	ratingAvg1 = ratingSum1 / float(len(ratingMatrixDict[userId1].keys()))
	ratingAvg2 = ratingSum2 / float(len(ratingMatrixDict[userId2].keys()))
	'''

	resultDict = collections.OrderedDict()
	resultDict[userId1] = ratingAvg1
	resultDict[userId2] = ratingAvg2

	return resultDict

def _calPcc(ratingMatrixDict, userId1, userId2, commonItemList, ratingAvgDict):
	nume = 0
	dino1 = 0
	dino2 = 0

	for item in commonItemList:
		nume += ((ratingMatrixDict[userId1][item].rating - ratingAvgDict[userId1]) * (ratingMatrixDict[userId2][item].rating - ratingAvgDict[userId2]))
		dino1 += ((ratingMatrixDict[userId1][item].rating - ratingAvgDict[userId1]) * (ratingMatrixDict[userId1][item].rating - ratingAvgDict[userId1]))
		dino2 += ((ratingMatrixDict[userId2][item].rating - ratingAvgDict[userId2]) * (ratingMatrixDict[userId2][item].rating - ratingAvgDict[userId2]))

	if nume == 0 or math.sqrt(float(dino1)*float(dino2)) == 0:
		return 0
	else:
		return nume / math.sqrt(float(dino1)*float(dino2))

def sortByPcc(pccDict):
	for key, value in pccDict.items():
		tempDict = value
        pccDict[key] = collections.OrderedDict(sorted(tempDict.items(), key=lambda t: t[1], reverse = True))

	return pccDict

def predictRating(outputDataTuples, ratingMatrixDict, topK, pccDict):
	for item in outputDataTuples:
		neighbors = pccDict[item.userId]

		totalPcc = 0
		totalNume = 0

		cnt = topK
		for key, value in neighbors.items():
			try:
				rating = ratingMatrixDict[key][item.itemId].rating
				totalNume += (value * rating)
				totalPcc += value
				topK -= 1
			except KeyError as e:
				continue

			if topK < 1:
				break

		if totalNume != 0 and totalPcc != 0:
			item.rating = int(round(totalNume / float(totalPcc)))

def writeRating(outputDataTuples, outputFile):
	for item in outputDataTuples:
		outputFile.write(str(item.userId) + "\t" + str(item.itemId) + "\t" + str(item.rating) + "\n")
	


if __name__ == '__main__':
	startTime = datetime.datetime.now()

	topK = 10

	# check if user inserted 3 arguments
	if len(sys.argv) != 3:
		print('\n* How to execute : ')
		print('python recommender.py [training_file_name] [test_file_name]\n')
		sys.exit(1)

	# get the values from the arguments
	trainingFileName = sys.argv[1]
	testFileName = sys.argv[2]

	trainingFileNum = int(filter(str.isdigit,trainingFileName))

	# open file
	trainingFile = fileOpen(trainingFileName, 'r')

	trainingDataTuples = getDataFromFile(trainingFile)

	ratingMatrixDict = collections.OrderedDict()

	assignRatingMatrix(ratingMatrixDict, trainingDataTuples)

	pccDict = calPcc(ratingMatrixDict)

	pccDict = sortByPcc(pccDict)

	testFile = fileOpen(testFileName, 'r')

	outputFileName = "u" + str(trainingFileNum) + ".base_prediction.txt"
	outputFile = fileOpen(outputFileName, 'w')

	outputDataTuples = getDataFromFile(testFile)

	predictRating(outputDataTuples,ratingMatrixDict, topK, pccDict)

	writeRating(outputDataTuples, outputFile)

	# close input file
	trainingFile.close()
	testFile.close()
	outputFile.close()

	endTime = datetime.datetime.now()

	print("learning time : " + str(endTime - startTime))
























