# -*- coding: utf-8 -*-
import sys 			#arvg, exit
import collections 	#orderedDict
import math 		#sqrt
import re 			#sub
import matplotlib.pyplot as plt

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
	for idx in range(0, len(inputObjects)-1):
		if idx % 100 == 0:
			print "connecting " + str(idx) + " / " + str(len(inputObjects)) + " object node..."
		for idx2 in range(idx+1, len(inputObjects)):
			directDensityReachable = checkDirectDensityReachable(inputObjects[idx], inputObjects[idx2], eps)

			if directDensityReachable:
				inputObjects[idx].pointing.append(inputObjects[idx2])
				inputObjects[idx2].pointing.append(inputObjects[idx])

		#if len(inputObjects[idx].pointing) < minPts:
		#	inputObjects[idx].pointing = []

def doClustering(inputObjects, clusterList, minPts, eps):
	print "\nstart clustering"
	for item in inputObjects:
		if item.cluster != -1:
			continue

		if len(item.pointing) >= minPts:
			currentCluster = []
			item.cluster = len(clusterList)
			currentCluster.append(item)
			
			for node in item.pointing:
				if node.cluster != -1:
					continue

				#node.cluster = item.cluster
				#currentCluster.append(node)

				if len(node.pointing) >= minPts:
					expandCluster(node, item.cluster, currentCluster, minPts)

			clusterList.append(currentCluster)



def expandCluster(nodeObject, clusterId, currentCluster, minPts):
	nodeObject.cluster = clusterId
	currentCluster.append(nodeObject)

	if len(nodeObject.pointing) < minPts:
		return

	for pointedNode in nodeObject.pointing:
		if pointedNode.cluster != -1 or len(pointedNode.pointing) < minPts:
			continue
		#if len(nodeObject.pointing) == 0:
		#	return
		expandCluster(pointedNode, clusterId, currentCluster, minPts)

def doClustering2(inputObjects, clusterList, minPts):
	for targetObject in inputObjects:
		if targetObject.cluster != -1 or len(targetObject.pointing) < minPts:
			continue

		currentCluster = []
		currentCluster.append(targetObject)
		clusterId = len(clusterList)

		expandCluster2(targetObject, clusterId, currentCluster, minPts)

		clusterList.append(currentCluster)
		
def expandCluster2(coreObject, clusterId, currentCluster, minPts):
	for neighborObject in coreObject.pointing:
		if neighborObject.cluster != -1:
			continue

		neighborObject.cluster = clusterId
		currentCluster.append(neighborObject)

		if len(neighborObject.pointing) >= minPts:
			expandCluster2(neighborObject, clusterId, currentCluster, minPts)

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
			outputFile.write(str(item.nodeId) + '\n')

		outputFile.close()

def showScatterChart(clusterList, numOfCluster):
	xCoorList = []
	yCoorList = []

	for item in clusterList:
		xCoors = []
		yCoors = []

		for node in item:
			xCoors.append(node.xCoor)
			yCoors.append(node.yCoor)
		xCoorList.append(xCoors)
		yCoorList.append(yCoors)

	colorList = ['red', 'yellow', 'green', 'blue', 'black', 'brown', 'purple', 'coral']

	for idx in range(0, numOfCluster):
		plt.scatter(xCoorList[idx], yCoorList[idx],c=colorList[idx % len(colorList)-1])
	plt.show()



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
	inputFileNum = int(filter(str.isdigit,inputFileNum))

	# open file
	inputFile = fileOpen(inputFileName, 'r')

	# get input objects
	inputObjects = getInputObjects(inputFile)



	# list of list for clusters
	clusterList = []
	
	connectObjectNodes(inputObjects, eps, minPts)

	#inputObjects.sort(key=lambda x: len(x.pointing), reverse=True)

	sys.setrecursionlimit(10000)

	#doClustering(inputObjects, clusterList, minPts, eps)
	doClustering2(inputObjects, clusterList, minPts)
	

	clusterList.sort(key=len, reverse=True)

	for idx in range(0, numOfCluster):
		print str(len(clusterList[idx])) + " size"

	writeClusters(clusterList, numOfCluster, inputFileNum)

	inputFile.close()

	showScatterChart(clusterList, numOfCluster)




































