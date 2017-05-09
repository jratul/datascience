# -*- coding: utf-8 -*-
import sys 			#arvg, exit
import collections 	#orderedDict
import math 		#sqrt
import re 			#sub

class ObjectNode():
	def __init__(self, nodeId, xCoor, yCoor):
		self.nodeId = nodeId
		self.xCoor = xCoor
		self.yCoor = yCoor
		self.cluster = -1
		self.pointing = []


# open files
def fileOpen(fileName, mode):
	try:
		file = open(fileName, mode)
		return file
	except FileNotFoundError as e:
		print('There is no file with name', fileName)
		sys.exit(1)

# get input objects
def getInputObjects(inputFile):
	inputObjects = []

	while True:
		line = inputFile.readline()

		if not line: break

		values = line.split()

		objectNode = ObjectNode(int(values[0]), float(values[1]), float(values[2]))

		inputObjects.append(objectNode)

	return inputObjects

def connectObjectNodes(inputObjects, eps, minPts):
	for idx in range(0, len(inputObjects)):
		if idx % 100 == 0:
			print "connecting " + str(idx) + " / " + str(len(inputObjects)) + " object node..."
		for idx2 in range(0, len(inputObjects)):
			directDensityReachable = checkDirectDensityReachable(inputObjects[idx], inputObjects[idx2], eps)

			if directDensityReachable:
				inputObjects[idx].pointing.append(inputObjects[idx2])

		if len(inputObjects[idx].pointing) < minPts:
			inputObjects[idx].pointing = []


def doClustering(inputObjects, clusterList, minPts, eps):
	tempInputObjects = inputObjects

	for idx in range(0, len(inputObjects)):
		if inputObjects[idx]['clustered'] == True:
			continue

		ptsCnt = 0
		cluster = []
		cluster.append(inputObjects[idx]['id'])

		notClusteredList = []

		for idx2 in range(0, len(tempInputObjects)):
			if inputObjects[idx]['id'] == tempInputObjects[idx2]['id']:
				continue

			directDensityReachable = checkDirectDensityReachable(inputObjects[idx], tempInputObjects[idx2], eps)

			if directDensityReachable:
				cluster.append(tempInputObjects[idx2]['id'])
			else:
				notClusteredList.append(tempInputObjects[idx2])

		if len(cluster) >= minPts:
			clusterList.append(cluster)
			tempInputObjects = notClusteredList

			for item in cluster:
				inputObjects[item]['clustered'] = True

def doClustering2(inputObjects, clusterList, minPts, eps):
	for idx in range(0, len(inputObjects)):
		cnt = 0
		for idx2 in range(0, len(inputObjects)):
			if idx == idx2:
				continue

			directDensityReachable = checkDirectDensityReachable(inputObjects[idx], inputObjects[idx2], eps)

			if directDensityReachable:
				cnt += 1

		inputObjects[idx]['pts'] = cnt

	return sorted(inputObjects, key=lambda k: k['pts'])

def doClustering3(inputObjects, clusterList, minPts, eps):
	print "start clustering"
	for item in inputObjects:
		if item.cluster != -1:
			continue

		if len(item.pointing) >= minPts:
			currentCluster = []
			item.cluster = len(clusterList)
			currentCluster.append(item.nodeId)
			
			for node in item.pointing:
				if node.cluster != -1:
					continue

				expandCluster(node, item.cluster, currentCluster)

			clusterList.append(currentCluster)



def expandCluster(nodeObject, clusterId, currentCluster):
	nodeObject.cluster = clusterId
	currentCluster.append(nodeObject.nodeId)

	for pointedNode in nodeObject.pointing:
		if nodeObject.cluster != -1 or len(nodeObject.pointing) ==0:
			return
		expandCluster(pointedNode, clusterId, currentCluster)









def checkDirectDensityReachable(coreObject, otherObject, eps):
	distance = calDistance(coreObject, otherObject)

	if distance < eps:
		return True
	else:
		return False

def calDistance(coreObject, otherObject):
	xPart = (coreObject.xCoor - otherObject.xCoor) * (coreObject.xCoor - otherObject.xCoor)
	yPart = (coreObject.yCoor - otherObject.yCoor) * (coreObject.yCoor - otherObject.yCoor)

	return math.sqrt(xPart + yPart)


def writeClusters(clusterList, numOfCluster, inputFileNum):
	for idx in range(0, numOfCluster):
		outputFileName = "input" + str(inputFileNum) + "_cluster_" + str(idx) + ".txt"
		outputFile = fileOpen(outputFileName, 'w')

		for item in clusterList[idx]:
			outputFile.write(str(item) + '\n')

		outputFile.close()




if __name__ == '__main__':
	# check if user inserted 5 arguments
	if len(sys.argv) != 5:
		print('\n* How to execute : ')
		print('python clustering.py [input_file] [n] [eps] [MinPts]\n')
		sys.exit(1)

	# get the values from the arguments
	inputFileName = sys.argv[1]
	numOfCluster = int(sys.argv[2])
	eps = float(sys.argv[3])
	minPts = int(sys.argv[4])

	inputFileNum = inputFileName
	#inputFileNum.replace("input", "")
	#inputFileNum.replace(".txt", "")
	#inputFileNum.strip("input.txt")
	#re.sub("\D", '', inputFileNum)
	#re.findall('\d+', inputFileNum)
	inputFileNum = int(filter(str.isdigit,inputFileNum))
	print inputFileNum

	# open file
	inputFile = fileOpen(inputFileName, 'r')

	# get input objects
	inputObjects = getInputObjects(inputFile)

	# list of list for clusters
	clusterList = []
	'''
	doClustering(inputObjects, clusterList, minPts, eps)

	clusterList.sort(key=len, reverse=True)

	idx = 0
	for cluster in clusterList:
		if idx == numOfCluster:
			break
		print(str(idx) + "-cluster : " + str(len(cluster)))
		print(cluster)
		print('\n')
		idx += 1
	'''

	'''
	inputObjects = doClustering2(inputObjects, clusterList, minPts, eps)

	for item in inputObjects:
		print(str(item['id']) + " : " + str(item['pts']))
	'''

	connectObjectNodes(inputObjects, eps, minPts)

	sys.setrecursionlimit(10000)

	doClustering3(inputObjects, clusterList, minPts, eps)

	clusterList.sort(key=len, reverse=True)

	for idx in range(0, numOfCluster):
		print str(len(clusterList[idx])) + " size"
		print clusterList[idx]
		print '\n'

	writeClusters(clusterList, numOfCluster, inputFileNum)

	inputFile.close()





































