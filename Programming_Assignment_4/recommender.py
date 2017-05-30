# -*- coding: utf-8 -*-
import sys 		#arvg, exit

class RatingTuple():
	def __init__(self, userId, itemId, rating, timeStamp):
		self.userId = userId
		self.itemId = itemId
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

def getTrainingData(trainingFile):
	trainingDataTuples = []

	while True:
		line = trainingFile.readline()

		if not line: break

		values = line.split()

		ratingTupleNode = RatingTuple(int(values[0]), int(values[1]), int(values[2]), int(values[3]))

		trainingDataTuples.append(ratingTupleNode)

	return trainingDataTuples

if __name__ == '__main__':
	# check if user inserted 3 arguments
	if len(sys.argv) != 3:
		print('\n* How to execute : ')
		print('python recommender.py [training_file_name] [test_file_name]\n')
		sys.exit(1)

	# get the values from the arguments
	trainingFileName = sys.argv[1]
	testFileName = sys.argv[2]

	# open file
	trainingFile = fileOpen(trainingFileName, 'r')

	trainingDataTuples = getTrainingData(trainingFile)

	for item in trainingDataTuples:
		print(item.userId, item.itemId, item.rating, item.timeStamp)

	# close input file
	trainingFile.close()
























