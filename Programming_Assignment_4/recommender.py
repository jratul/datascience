# -*- coding: utf-8 -*-
import sys 				#arvg, exit
import collections		#orderedDict
import math 			#sqrt
import datetime 		#now
from operator import itemgetter
import random

# class for rating tuple
class RatingTuple():
	def __init__(self, userId, itemId, rating, timeStamp):
		'''
		userId : user's id
		itemId : movie's id
		rating : the rating that user has given to movie
		timeStamp : the time when user gave the rating to movie
		'''
		self.userId = userId
		self.itemId = itemId
		self.rating = rating
		self.timeStamp = timeStamp

# class for rating matrix cell
class RatingMatrixCell():
	'''
	rating : the rating that user has given to movie
	timeStamp : the time when user gave the rating to movie
	'''
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

# make tuple list by the data from file
def getDataFromFile(file):
	dataTuples = []

	while True:
		line = file.readline()

		if not line: break

		values = line.split()

		'''
		values[0] : user id
		values[1] : movie id
		values[2] : rating
		values[3] : timestamp
		'''
		ratingTupleNode = RatingTuple(int(values[0]), int(values[1]), int(values[2]), int(values[3]))

		dataTuples.append(ratingTupleNode)

	return dataTuples

# assign value into rating matrix
# I'll use dictionary for rating matrix, instead of the 2-dimensional array.
# Because rating matrix will be a sparse matrix
def assignRatingMatrix(ratingMatrixDict, trainingDataTuples):
	for item in trainingDataTuples:
		if item.userId not in ratingMatrixDict:
			ratingMatrixDict[item.userId] = collections.OrderedDict()
		ratingMatrixDict[item.userId][item.itemId] = RatingMatrixCell(item.rating, item.timeStamp)

# calculate Pearson Correlation Coefficient
def calPcc(ratingMatrixDict):
	pccDict = collections.OrderedDict()
	maximumIdx = len(ratingMatrixDict.keys())
	for idx in range(0, maximumIdx):
		# every 10 item, show the progress
		if idx % 10 == 0:
			print(str(idx) + " / " + str(maximumIdx) + " calculating PCC")
		for idx2 in range(idx+1, maximumIdx):
			key1 = ratingMatrixDict.keys()[idx]
			key2 = ratingMatrixDict.keys()[idx2]

			# get intersection from user1, user2's rating history
			set1 = set(ratingMatrixDict[key1].keys())
			set2 = set(ratingMatrixDict[key2].keys())
			commonItemList = list(set1.intersection(set2))

			# if there is no common item, they are not neighbor.
			if(len(commonItemList) == 0):
				continue

			# calculate rating average of two users
			ratingAvgDict = calRatingAvg(ratingMatrixDict, key1, key2, commonItemList)

			# calculate Pearson correlation coefficient 
			pccValue = _calPcc(ratingMatrixDict, key1, key2 ,commonItemList, ratingAvgDict)

			if key1 not in pccDict:
				pccDict[key1] = collections.OrderedDict()

			if key2 not in pccDict:
				pccDict[key2] = collections.OrderedDict()

			pccDict[key1][key2] = pccValue
			pccDict[key2][key1] = pccValue

	return pccDict

# calculate rating average of two users
def calRatingAvg(ratingMatrixDict, userId1, userId2, commonItemList):
	ratingSum1 = 0
	ratingSum2 = 0

	for item in commonItemList:
		ratingSum1 += ratingMatrixDict[userId1][item].rating
		ratingSum2 += ratingMatrixDict[userId2][item].rating

	ratingAvg1 = ratingSum1 / float(len(commonItemList))
	ratingAvg2 = ratingSum2 / float(len(commonItemList))

	resultDict = collections.OrderedDict()
	resultDict[userId1] = ratingAvg1
	resultDict[userId2] = ratingAvg2

	return resultDict

# calculate Pearson correlation coefficient value
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

# sort neighbor group by pcc value
def sortByPcc(pccDict):
	for key, value in pccDict.items():
		tempDict = value
        pccDict[key] = collections.OrderedDict(sorted(tempDict.items(), key=lambda t: t[1], reverse = True))
        #pccDict[key] = dict(sorted(tempDict.items(), key=itemgetter(1), reverse = True))

	return pccDict

# predict rating
def predictRating(outputDataTuples, ratingMatrixDict, topK, pccDict): 
	for item in outputDataTuples:
		neighbors = pccDict[item.userId]

		totalPcc = 0
		totalNume = 0

		# compare with top k neighbors
		# I used weighted sum here.
		# If neighbor has higher pcc value, the rating of that neighbor will affect more.
		cnt = topK
		#for key, value in neighbors.items():
		for item2 in sorted(neighbors.items(), key=lambda t: t[1], reverse = True):
			if item2[1] < 0:
				break
			try:
				#rating = ratingMatrixDict[key][item.itemId].rating
				rating = ratingMatrixDict[item2[0]][item.itemId].rating
				totalNume += (item2[1] * rating)
				totalPcc += item2[1]
				cnt -= 1
			except KeyError as e:
				continue

			if cnt < 1:
				break

		if totalNume != 0 and totalPcc != 0:
			item.rating = int(round(totalNume / float(totalPcc)))

		if item.rating < 1 or item.rating > 5:
			print('error item')
			print('user id : ' + str(item.userId) + ', item id : ' + str(item.itemId) + ', rating : ' + str(item.rating))

		if (totalNume == 0 or totalPcc == 0) and (item.rating < 1 or item.rating > 5):
			tempSum = 0
			cnt2 = 0

			for key, value in ratingMatrixDict.items():
				for key2, value2 in value.items():
					if key2 == item.itemId:
						tempSum += value2.rating
						cnt2 += 1
			if cnt2 != 0:
				item.rating = int(round(tempSum / float(cnt2)))
			else:
				item.rating = random.randrange(1,6)




# write rating values into output file
def writeRating(outputDataTuples, outputFile):
	for item in outputDataTuples:
		outputFile.write(str(item.userId) + "\t" + str(item.itemId) + "\t" + str(item.rating) + "\n")

if __name__ == '__main__':
	# to check running time
	startTime = datetime.datetime.now()

	# the number of neighbor
	topK = 10

	# check if user inserted 3 arguments
	if len(sys.argv) != 3:
		print('\n* How to execute : ')
		print('python recommender.py [training_file_name] [test_file_name]\n')
		sys.exit(1)

	# get the values from the arguments
	trainingFileName = sys.argv[1]
	testFileName = sys.argv[2]

	# extract input file number from input file name for output file name
	trainingFileNum = int(filter(str.isdigit,trainingFileName))

	# open training file
	trainingFile = fileOpen(trainingFileName, 'r')

	# get data tuples from traing file
	trainingDataTuples = getDataFromFile(trainingFile)

	# make dictionary for rating matrix
	ratingMatrixDict = collections.OrderedDict()

	# assign rating values into rating matrix
	assignRatingMatrix(ratingMatrixDict, trainingDataTuples)

	# calculate Pearson correlation coefficient
	pccDict = calPcc(ratingMatrixDict)

	# sort neighbor groups by Pearson correlation coefficient
	#pccDict = sortByPcc(pccDict)

	pccFile = fileOpen("pccdict.txt", 'w')

	#for key, value in pccDict[1].items():
	#	print(str(key) + ":" +str(value))

	'''
	for key, value in pccDict.items():
		pccFile.write(str(key) + '\n')

		for key2, value2 in value.items():
			pccFile.write(str(key2) + ":" + str(value2) + "\t")
		pccFile.write('\n\n')
	'''

	# open test file
	testFile = fileOpen(testFileName, 'r')

	# open output file
	outputFileName = "u" + str(trainingFileNum) + ".base_prediction.txt"
	outputFile = fileOpen(outputFileName, 'w')

	# read data tuples from test file
	outputDataTuples = getDataFromFile(testFile)

	# predict rating
	predictRating(outputDataTuples,ratingMatrixDict, topK, pccDict)

	# write rating values into output file
	writeRating(outputDataTuples, outputFile)

	# close input file
	trainingFile.close()
	testFile.close()
	outputFile.close()

	# to check running time
	endTime = datetime.datetime.now()

	# show running time
	print("running time : " + str(endTime - startTime))
























