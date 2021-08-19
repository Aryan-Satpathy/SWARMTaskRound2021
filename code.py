import sys
from api import *
from time import sleep
import numpy as np
import random as rnd
import cv2
import math

#######    YOUR CODE FROM HERE #######################

CommsFilePath = r'Status.txt'
BlackFilePath = r'Gone.txt'
stringFormat = 'i : Status      jj : len\n'
# Index helper :012345678901234567890123

while True : 
	try : 
		CommsFile = open(CommsFilePath, 'r+')
		break
	except : 
		_file = open(CommsFilePath, 'w')
		_file.write('''0 : Sleeping       :    
1 : Sleeping       :    
2 : Sleeping       :    
3 : Sleeping       :    
4 : Sleeping       :    
5 : Sleeping       :    
6 : Sleeping       :    
7 : Sleeping       :    

''')
		_file.flush()
		_file.close()
while True : 
	try : 
		BlackFile = open(BlackFilePath, 'r+')
		break
	except : 
		_file = open(BlackFilePath, 'w')
		_file.write('None, ')
		_file.flush()
		_file.close()

numbots = get_numbots()
	
goalList = get_greenZone_list()

blackList = []

NeighbourMap = {(-1, -1) : 1, (0, -1) : 2, (1, -1) : 3, (1, 0) : 4, (1, 1) : 5, (0, 1) : 6, (-1, 1) : 7, (-1, 0) : 8}

obsList = get_obstacles_list()

redList = get_redZone_list()

def getPathLenStr(pathLen) : 
	a = pathLen // 100
	b = (pathLen % 100) // 10
	c = (pathLen % 10) 
	return '{}{}{}'.format(a, b, c)

def getGoalIDStr(goalID) : 
	b = goalID // 10
	c = goalID % 10 
	return '{}{}'.format(b, c)

def decodeComms(message) : 
	botID = int(message[0])
	status = message[4 : 15].rstrip()
	try : 
		goalID = int(message[16 : 18])
	except : 
		goalID = None
	pathLen = 0
	try : 
		pathLen = int(message[21 : ])
	except : 
		pass
	return (botID, status, goalID, pathLen)

def isValid(pos, obsList) : 
	for obs in obsList : 
		if liesIn(pos, obs) : 
			return False
	return True

def decode(pos1, pos2) : 
	delY , delX = pos2[0] - pos1[0], pos2[1] - pos1[1]
	return NeighbourMap[delX, delY]

def reconstruct_path(cameFrom, current) :
	total_path = []
	prev = cameFrom[current]
	
	total_path.append(decode(prev, current))

	while prev in cameFrom : 
		prev, current = cameFrom[prev], cameFrom[current]
		total_path.append(decode(prev, current))
	
	return total_path[ : : -1]

	'''
    total_path = [current]
    while current in cameFrom:
        current = cameFrom[current]
        total_path.append(current)
    return total_path[ : : -1]
	'''
	
def A_Star(start, goal, h, obsList, redList) : 
    # The set of discovered nodes that may need to be (re-)expanded.
    # Initially, only the start node is known.
    # This is usually implemented as a min-heap or priority queue rather than a hash-set. 
    
	openSet = [start]

    # For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from start
    # to n currently known.
	cameFrom = {}

    # For node n, gScore[n] is the cost of the cheapest path from start to n currently known.
	gScore = [[math.inf for i in range(200)] for j in range(200)]
	gScore[start[0]][start[1]] = 0

    # For node n, fScore[n] := gScore[n] + h(n). fScore[n] represents our current best guess as to
    # how short a path from start to finish can be if it goes through n.
	fScore = [[math.inf for i in range(200)] for j in range(200)]
	fScore[start[0]][start[1]] = h(start, goal)

	while len(openSet) :
        # print(len(openSet))
        # This operation can occur in O(1) time if openSet is a min-heap or a priority queue
		current = min(openSet, key = lambda pos : fScore[pos[0]][pos[1]])                                       # Get node from openSet with min fScore
		if current == goal :            
			print("Cost = {}".format(gScore[current[0]][current[1]]))
			return reconstruct_path(cameFrom, current)

		openSet.remove(current)
        # neighbours = [(-1, -1), ]
		neighbours = [(x, y) for x in range(-1, 2) for y in range(-1, 2) if (not(x == 0 and y == 0)) and 0 <= current[0] + x < 200 and 0 <= current[1] + y < 200 and isValid((current[0] + x, current[1] + y), obsList)]
		for neighbor in neighbours :
            # d(current,neighbor) is the weight of the edge from current to neighbor
            # tentative_gScore is the distance from start to the neighbor through current
			x, y = neighbor
			
			costMultiplier = 1
			
			for red in redList : 
				if liesIn((current[0] + x, current[1] + y), red) : 
					costMultiplier = 2
					break

			tentative_gScore = gScore[current[0]][current[1]] + costMultiplier * [1, 1.4][x * y]
			if tentative_gScore < gScore[current[0] + x][current[1] + y] : 
				# This path to neighbor is better than any previous one. Record it!
				cameFrom[(current[0] + x, current[1] + y)] = current
				gScore[current[0] + x][current[1] + y] = tentative_gScore
				fScore[current[0] + x][current[1] + y] = gScore[current[0] + x][current[1] + y] + h((current[0] + x, current[1] + y), goal)
				if (current[0] + x, current[1] + y) not in openSet : 
					openSet.append((current[0] + x, current[1] + y))

    # Open set is empty but goal was never reached
	return None

def heuristic(pos, goal) : 
	return distance(pos, goal)

def distance(pos1, pos2) : 
	return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

def liesIn(pos, rect) : 
	tl, br = rect[0], rect[2]

	xmin, ymin = tl
	xmax, ymax = br

	x, y = pos

	return (xmin <= x <= xmax) and (ymin <= y <= ymax)

class Node : 
	def  __init__(self, pos) : 
		self.pos = pos
		self.cameFrom = None 
		self.id = None

class Graph : 
	def __init__(self, step) : 
		self.step = step
		self.nodes = []
		self.occupiedPos = []
		self.goalNodes = {}
		self.edges = []
		self.len = 0
		self.obsList = None
		self.map = None
	def addNode(self, node) : 
		if node.pos in self.occupiedPos : 
			return False
		node.id = self.len
		self.nodes.append(node)
		self.occupiedPos.append(node.pos)
		self.len += 1
		return node.id
	def getClosestNode(self, pos) : 
		return min(self.nodes, key = lambda node : distance(node.pos, pos))
	def canMakeLine(self, pos1, pos2) :
		for obs in self.obsList : 
			flag = Graph._canMakeLine(pos1, pos2, obs)
			if flag == False : 
				return False
		return True
	@staticmethod
	def _canMakeLine(pos1, pos2, obs) : 
		(xmin, ymin), (xmax, ymax) = obs[0], obs[2]

		Y = Graph.getY(pos1, pos2, xmin)
		if Y != None and ymin <= Y <= ymax : 
			if min(pos1[1], pos2[1]) <= Y <= max(pos1[1], pos2[1]) : 
				return False
		Y = Graph.getY(pos1, pos2, xmax)
		if Y != None and ymin <= Y <= ymax : 
			if min(pos1[1], pos2[1]) <= Y <= max(pos1[1], pos2[1]) : 
				return False
		X = Graph.getX(pos1, pos2, ymin)
		if X != None and xmin <= X <= xmax : 
			if min(pos1[0], pos2[0]) <= X <= max(pos1[0], pos2[0]) : 
				return False
		X = Graph.getX(pos1, pos2, ymax)
		if X != None and xmin <= X <= xmax : 
			if min(pos1[0], pos2[0]) <= X <= max(pos1[0], pos2[0]) : 
				return False

		return True
	def createNodeBetween(self, node1, pos2) : 
		pos1 = node1.pos
		D = distance(pos1, pos2)
		if D <= self.step : 
			finalPos = pos2
		else :
			m, n = D - self.step, self.step
			m /= D
			n /= D
			finalPos = int(pos1[0] * m + pos2[0] * n), int(pos1[1] * m + pos2[1] * n)
		
		node = Node(finalPos)

		success = self.addNode(node)

		if success : 
			node.cameFrom = node1
			self.edges.append((node.id, node1.id))

		return success
	def expand (self) : 
		x, y = rnd.randint(0, 199), rnd.randint(0, 199)

		while True  :
			if False in (self.map[(x, y)] == np.array((0, 0, 0))) : 
				break
			
			x, y = rnd.randint(0, 199), rnd.randint(0, 199)

		closestNode = self.getClosestNode((x, y))

		if self.canMakeLine(closestNode.pos, (x, y)) : 
			success = self.createNodeBetween(closestNode, (x, y))
			return success
		return self.expand()

	def bias(self, goal) : 
		
		x, y = goal

		closestNode = self.getClosestNode((x, y))

		if self.canMakeLine(closestNode.pos, (x, y)) : 
			success = self.createNodeBetween(closestNode, (x, y))
			return success
		return False
	def checkGoals (self) : 
		greenList = get_greenZone_list()
		l = len(greenList)

		foundAtLeastOne = False

		for ind in range(self.len) : 
			for ind2 in range(l) : 
				if liesIn(self.occupiedPos[ind], greenList[ind2]) : 
					self.goalNodes[ind2] = ind
					foundAtLeastOne = True
		
		return foundAtLeastOne
	def constructPath(self, goalInd) : 
		if goalInd in self.goalNodes : 
			print('Constructing Path')
			path = []

			curr = self.nodes[self.goalNodes[goalInd]]
			path.append(curr.pos)
			while curr.cameFrom != None : 
				curr = curr.cameFrom
				path.append(curr.pos)
			
			return path[ : : -1]
		return False
	@staticmethod
	def getX(pos1, pos2, y) : 
		if pos1[1] - pos2[1] == 0 :
			return None
		x = pos2[0] + (y - pos2[1]) * (pos1[0] - pos2[0]) / (pos1[1] - pos2[1])

		return x

	@staticmethod
	def getY(pos1, pos2, x) :
		if pos1[0] - pos2[0] == 0 :
			return None
		y = pos2[1] + (x - pos2[0]) * (pos1[1] - pos2[1]) / (pos1[0] - pos2[0])

		return y

## THEIR CODE BELOW, DONOT CROSS THIS LINE
########## Default Level 1 ##########
'''
def level1(botId):
	
	mission_complete=False
	botId=0
	while(not mission_complete):
		successful_move, mission_complete = send_command(botId,r.randint(1,8))
		if successful_move:
			print("YES")
		else:
			print("NO")
		if mission_complete:
			print("MISSION COMPLETE")
		pos=get_botPose_list()
		print(pos[0])
'''
'''
def level1(botId) : 
	toSeek = botId * len(stringFormat)

	CommsFile.write('{} : Calculating\n'.format(botId))
	CommsFile.seek(toSeek)

	while True :
		try : 
			_map = get_Map()
			break
		except : 
			pass

	RRTGraph = Graph(10)

	RRTGraph.map = _map
	RRTGraph.obsList = get_obstacles_list()

	start = tuple(get_botPose_list()[botId])

	print('Start Color : {}'.format(RRTGraph.map[start]))
	print('One obstacle rect : {}'.format(RRTGraph.obsList[0]))

	startNode = Node(start)

	RRTGraph.addNode(startNode)

	pathFound = False

	Choices = [0] * 2000 + [1] * 20

	checkInterval = 100
	i = 0
	while not pathFound : 
		choice = rnd.choice(Choices)

		if choice == 0 :
			RRTGraph.expand()
		else : 
			goal = (199, 199)
			RRTGraph.bias(goal)
		
		i += 1

		if not (i % checkInterval) : 
			pathFound = RRTGraph.checkGoals()
	
	path = None
	if pathFound : 
		# path = RRTGraph.constructPath(RRTGraph.goalNodes[list(RRTGraph.goalNodes.keys())[0]])
		print(RRTGraph.goalNodes)
		GoAl = list(RRTGraph.goalNodes.keys())[0]
		print(list(RRTGraph.goalNodes.keys())[0] == 0)
		print(0 in RRTGraph.goalNodes)
		path = RRTGraph.constructPath(GoAl)
	
	print(path)

	TotalPath = []

	for i in range(len(path) - 1) : 
		TotalPath += A_Star(path[i], path[i + 1], heuristic, RRTGraph.obsList)

	print(TotalPath)

	TotalPath2 = A_Star(start, (197, 197), heuristic, RRTGraph.obsList)

	print(TotalPath2)

	CommsFile.write('{} : Travelling \n'.format(botId, 0))
	CommsFile.seek(toSeek)

	for comm in TotalPath : 
		successful_move, mission_complete = send_command(botId,comm)
		if successful_move:
			print("YES")
		else:
			print("NO")
		if mission_complete:
			print("MISSION COMPLETE")
			CommsFile.write('{} : Sleeping   \n'.format(botId, 0))
			CommsFile.seek(toSeek)
			return False
	print(get_botPose_list()[botId])
	CommsFile.write('{} : Sleeping   \n'.format(botId, 0))
	CommsFile.seek(toSeek)
	return True
'''

def selectGoal(start, goalList, blackList) : 
	minDistance = math.inf
	minGoal = 'not Possible'
	for ind in range(len(goalList)) : 
		if ind not in blackList : 
			tl, br = goalList[ind][0], goalList[ind][1]

			center = (tl[0] + br[0]) // 2, (tl[1] + br[1]) // 2

			D = distance(center, start)

			if minDistance > D : 
				minDistance = D
				minGoal = ind
	return minGoal

def level1(botId) : 

	# Seek to the pos in file where current bot's info is present
	toSeek = (botId) * len(stringFormat)

	# Get list of bot Posi
	botPosList = get_botPose_list()

	start = tuple(botPosList[botId])

	CommsFile.seek(toSeek)

	'''
	CommsFile.seek(0)
	blackList = eval(CommsFile.read(len(stringFormat)))
	CommsFile.seek(toSeek)
	'''

	while True :
		# Calculating Path
		print('Calculating')
		# Update so in file
		CommsFile.write('{} : Calculating    :    \n'.format(botId))
		CommsFile.flush()
		CommsFile.seek(toSeek)

		# Get Goal based on blacklist and proximity
		ind = selectGoal(start, goalList, blackList)

		# Unexpected Scenario, shouldnt happen at all
		if ind is None : 
			print('Got None, blacklist = ', blackList)

		# No goal possible, send to sleep
		if ind == 'not Possible' : 
			print('{} Sleeping'.format(botId))
			CommsFile.write('{} : Sleeping       :    \n'.format(botId))
			CommsFile.flush()
			return False

		toBreak = False

		# Goal center coords
		goal = (goalList[ind][0][0] + goalList[ind][2][0]) // 2, (goalList[ind][0][1] + goalList[ind][2][1]) // 2

		# Calculate path to goal center
		path = A_Star(start, goal, heuristic, obsList, redList)

		# Update file with calculated goal ind and path len
		CommsFile.write('{} : Calculated  {} : {}\n'.format(botId, getGoalIDStr(ind), getPathLenStr(len(path))))
		CommsFile.flush()
		CommsFile.seek(toSeek)

		# Wait till all bots have finished 'Calculating'
		wait = True
		while wait : 
			BlackFile.seek(0)
			
			# BlackList evaluated
			_Black = eval(BlackFile.read())

			# Add non existing goals to blackList
			blackList.extend([b for b in _Black if b not in blackList and b is not None])

			# Read all statuses (only 'numbots' statuses)
			CommsFile.seek(0)
			Statuses = CommsFile.readlines()[ : numbots]

			CommsFile.seek(toSeek)

			_Statuses = []
			_Goals = []
			_pathLens = []

			# By default do not wait
			wait = False

			# Iterate over statuses
			# Decode comms format to get values
			for status in Statuses : 
				bot, _status, goalTo, pathLen = decodeComms(status[ : -1])
				# If One bot's status is calculating, MUST WAIT
				if _status == 'Calculating' :
					wait = True 
					break
				# If someone is travelling while we are waiting, we must take their goal and add to our blacklist
				if _status == 'Travelling' :
					if goalTo not in blackList : blackList.append(goalTo)
				# Append all info
				_Statuses.append(_status)
				_Goals.append(goalTo)
				_pathLens.append(pathLen)
			
			# Sleep, bcoz you got time
			time.sleep(0.005)

		# FROM HERE ON, ALL BOTS HAVE ATLEAST REACHED STAGE 'CALCULATED' or 'TRAVELLING' or ARE DONE ('SLEEPING')
		
		# List, rather dictionary of unique goals sought after
		uniqueGoals = {}

		# print(_Statuses, _Goals, _pathLens)

		# Bots that need to recalculate path
		ToRecalculate = []

		for i in range(numbots) :
			# goal of some bot (may not even exist == None)
			goalTo = _Goals[i]

			# If goal in blacklist, current bot must recalculate
			if goalTo in blackList : 
				ToRecalculate.append(i)
				continue

			# If valid comms
			if goalTo is not None and _pathLens[i] != 0 :
				# If already sought after
				if goalTo in uniqueGoals :
					# Get currently shortest path to that goal and the bot who has that path 
					minD, b = uniqueGoals[goalTo]
					# If current is even shorter
					if _pathLens[i] <= minD : 
						# Recalculate prev bot, HAHA
						ToRecalculate.append(b)
						# update unique goals dict
						uniqueGoals[goalTo] = (_pathLens[i], i)
					else : 
						ToRecalculate.append(i)
				# First bot iterated, going after this goal, take it as reference
				else : 
					uniqueGoals[goalTo] = (_pathLens[i], i)
		
		print('To recalculate : ', ToRecalculate)
		
		# If me not in ToRecalucate, Imma head out
		if botId not in ToRecalculate : 
			toBreak = True
		
		# Remove this
		# toBreak = True

		if toBreak : 
			break

		# THOSE WHO HAVE TO RECALCULATE REACH HERE

		# For all those who are recalculating, the unique goals are taken by other bots by now so add to blacklist
		for G in uniqueGoals : 
			if G not in blackList : blackList.append(G)

	CommsFile.write('{} : Travelling  {} :    \n'.format(botId, getGoalIDStr(ind)))
	CommsFile.flush()
	CommsFile.seek(toSeek)

	BlackFile.seek(0, 2)

	BlackFile.write('{}, '.format(ind))
	BlackFile.flush()
	print('Writing To File {}'.format(ind))

	time.sleep(0.005)

	blackList.append(ind)

	# Tavelling
	for comm in path : 
		successful_move, mission_complete = send_command(botId,comm)
		if successful_move:
			# print("YES")
			pass
		else:
			# print("NO")
			pass
		if mission_complete:
			print("MISSION COMPLETE")
			CommsFile.write('{} : Sleeping       :    \n'.format(botId))
			CommsFile.flush()
			
			ManageGoneTxt = open(BlackFilePath, 'w')
			ManageGoneTxt.write('None, ')
			ManageGoneTxt.flush()
			ManageGoneTxt.close()
			return False
	
	# CommsFile.write('{} : Sleeping      :    \n'.format(botId, 0))
	# CommsFile.seek(toSeek)
	
	# Finish, POG
	return True

def level2(botId) : 
	toLoop = True
	while toLoop :
		toLoop = level1(botId)
	
	print('Bot {} has done its part'.format(botId))

def level3(botId) : 
	# obs list same for all bots
	# pog

	print('OBS LIST\n{}	: {}'.format(botId, get_obstacles_list()))
	level2(botId)	

def level4(botId):
	level2(botId)

def level5(botId):
	level2(botId)

def level6(botId):    
	level2(botId)


#######    DON'T EDIT ANYTHING BELOW  #######################

if  __name__=="__main__":
	botId = int(sys.argv[1])
	level = get_level()
	if level == 1:
		level1(botId)
	elif level == 2:
		level2(botId)
	elif level == 3:
		level3(botId)
	elif level == 4:
		level4(botId)
	elif level == 5:
		level5(botId)
	elif level == 6:
		level6(botId)
	else:
		print("Wrong level! Please restart and select correct level")

CommsFile.close()
BlackFile.close()
