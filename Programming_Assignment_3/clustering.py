# -*- coding: utf-8 -*-
import sys 		#arvg, exit
import math 	#sqrt
 
# class for data object
class ObjectNode():
	'''
	nodeId : node's id
	xCoor : node's x coordinate
	yCoor : node's y coordinate
	cluster : node's cluster number. if it is -1, the node is not in cluster.
	pointing : other reachable(in eps) nodes from this node
	'''
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

		'''
		values[0] : node's id
		values[1] : node's x coordinate
		values[2] : node's y coordinate
		'''
		objectNode = ObjectNode(int(values[0]), float(values[1]), float(values[2]))

		inputObjects.append(objectNode)

	return inputObjects

# connect reachable objects
# If the distance of point A, and B is smaller than eps,
# they are reachable to each other.
def connectObjectNodes(inputObjects, eps, minPts):
	for idx in range(0, len(inputObjects)-1):
		# This process takes long time, if there are too many data objects.
		# To inform the user how much proceeded, print the number of objects.
		if idx % 100 == 0:
			print "connecting " + str(idx) + " / " + str(len(inputObjects)) + " object node..."

		# If the pair of objects are reachable, add each other into 'pointing' list.
		for idx2 in range(idx+1, len(inputObjects)):
			directDensityReachable = checkReachable(inputObjects[idx], inputObjects[idx2], eps)

			if directDensityReachable:
				inputObjects[idx].pointing.append(inputObjects[idx2])
				inputObjects[idx2].pointing.append(inputObjects[idx])

# check if the pair of objects are reachable
# If the distance of the two points is less than eps,
# they are reachable to each other.
def checkReachable(coreObject, otherObject, eps):
	distance = calDistance(coreObject, otherObject)

	if distance <= eps:
		return True
	else:
		return False

# calculate euclidean distance of the two points
def calDistance(coreObject, otherObject):
	xPart = (coreObject.xCoor - otherObject.xCoor) * (coreObject.xCoor - otherObject.xCoor)
	yPart = (coreObject.yCoor - otherObject.yCoor) * (coreObject.yCoor - otherObject.yCoor)

	return math.sqrt(xPart + yPart)

# DBSCAN clustering
def doClustering(inputObjects, clusterList, minPts):
	#It scans every node sequentially.
	for targetObject in inputObjects:
		'''
		If the cluster value of target object is not -1,
		it means the target object is already in a specific cluster.
		And if the number of reachable objects from target object is less than minPts,
		it means the target object is not core point.
		In these above two cases, the target object can't expand the cluster.
		'''
		if targetObject.cluster != -1 or len(targetObject.pointing) < minPts:
			continue

		'''
		If the target object is core point, a new cluster will be formed.
		The target object will be put into the new cluster,
		and the cluster value of the target object will be assigned.
		'''
		currentCluster = []
		currentCluster.append(targetObject)
		clusterId = len(clusterList)
		targetObject.cluster = clusterId

		'''
		Because the target object is core point, it will expand the cluster.
		'''
		expandCluster(targetObject, clusterId, currentCluster, minPts)

		'''
		After the end of expanding cluster,
		the cluster will be saved in the cluster list.
		'''
		clusterList.append(currentCluster)

# expand cluster
def expandCluster(coreObject, clusterId, currentCluster, minPts):
	# visit every neighbor object of the core object
	for neighborObject in coreObject.pointing:
		# If the neighbor object is already in a specific cluster, continue
		if neighborObject.cluster != -1:
			continue

		# Otherwise, the neighbor object will be put into the current cluster.
		neighborObject.cluster = clusterId
		currentCluster.append(neighborObject)

		# check if the number of neighbor objects is more than minPts.
		# If then, expand the cluster recursively.
		if len(neighborObject.pointing) >= minPts:		
			expandCluster(neighborObject, clusterId, currentCluster, minPts)

# write the clusters into the output files
def writeClusters(clusterList, numOfCluster, inputFileNum):
	for idx in range(0, numOfCluster):
		outputFileName = "input" + str(inputFileNum) + "_cluster_" + str(idx) + ".txt"
		outputFile = fileOpen(outputFileName, 'w')

		for item in clusterList[idx]:
			outputFile.write(str(item.nodeId) + '\n')

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

	# extract input file number from input file name for output file name
	inputFileNum = inputFileName
	inputFileNum = int(filter(str.isdigit,inputFileNum))

	# open file
	inputFile = fileOpen(inputFileName, 'r')

	# get input objects
	inputObjects = getInputObjects(inputFile)

	# list of list for clusters
	clusterList = []
	
	# connecting the reachable pairs of nodes 
	connectObjectNodes(inputObjects, eps, minPts)

	# increase the recursion limit of python
	sys.setrecursionlimit(10000)

	# do clustering
	doClustering(inputObjects, clusterList, minPts)
	
	# sort to print TOP K clusters
	clusterList.sort(key=len, reverse=True)

	# print TOP K clusters
	for idx in range(0, numOfCluster):
		print str(len(clusterList[idx])) + " size"

	# write clusters into output files
	writeClusters(clusterList, numOfCluster, inputFileNum)

	# close input file
	inputFile.close()




































