import sys
import math
import copy
import random

class PCA:
	def __init__(self):
		self.something = list()

	def read_data(self):
		return

class Fastmap:
	def __init__(self):
		self.target_space = list()
		for i in range(10):
			temp = list()
			for j in range(2):
				temp.append(0)
			self.target_space.append(temp)

		self.object_space = list()
		
		for i in range(10):
			temp = list()
			for j in range(10):
				temp.append(0)
			self.object_space.append(temp)
		self.o_a = -1
		self.o_b = -1
		self.curr_col = -1


	# reads a file and returns a list of points
	def read_data(self):
		with open('fastmap-data.txt', 'r') as rawdata:
			lines = rawdata.readlines()
			for line in lines:
				if line != '\n':
					obj1, obj2, distance = (int(s) for s in line.split())
					self.object_space[obj1-1][obj2-1] = distance
					self.object_space[obj2-1][obj1-1] = distance

	def choose_furthest_objects(self):
		o_a = 1
		o_b = -1
		max_distance = -1
		for i in range (6):
			for j in range(10):
				if self.object_space[o_a-1][j] > max_distance:
					o_b = j+1
					max_distance = self.object_space[o_a-1][j]
			temp = o_a
			o_a = o_b
			o_b = temp
		self.o_a = o_a
		self.o_b = o_b
		print (self.o_a, self.o_b)

	def hyperplane_furthest_objects(self):
		o_a = 1
		o_b = 2
		max_distance = -1
		for i in range (6):
			for j in range(10):
				if self.hyperplane_distance(o_a, j+1) > max_distance:
					o_b = j+1
					max_distance = self.hyperplane_distance(o_a, j+1)
			temp = o_a
			o_a = o_b
			o_b = temp
		self.o_a = o_a
		self.o_b = o_b
		print (self.o_a, self.o_b)

	# o_i index is from 1-10
	def individual_projected_distance(self, o_i):
		return ( (self.object_space[o_i-1][self.o_a-1]**2 + 
			self.object_space[self.o_b-1][self.o_a-1]**2 - 
			self.object_space[o_i-1][self.o_b-1]**2) / 
			(2*self.object_space[self.o_b-1][self.o_a-1]))

	def hyperplane_projected_distance(self, o_i):
		return ( (self.hyperplane_distance(self.o_a, o_i)**2 + 
			self.hyperplane_distance(self.o_a, self.o_b)**2 - 
			self.hyperplane_distance(self.o_b, o_i)**2) / 
			(2*self.hyperplane_distance(self.o_a, self.o_b)))

	def hyperplane_distance(self, o_x, o_y):
		return math.sqrt( (self.object_space[o_x-1][o_y-1])**2 - (self.target_space[o_x-1][self.curr_col-1] - self.target_space[o_y-1][self.curr_col-1])**2 )

	def set_column_to_zero(self):
		for i in range(10):
			self.target_space[i][self.curr_col] = 0

	def fastmap(self, k):
		if k <= 0:
			for i in range (10):
				print (self.target_space[i])
			print ("return 1")
			return
		else:
			self.curr_col += 1

		if self.curr_col == 0:
			self.choose_furthest_objects()
			if self.object_space[self.o_a-1][self.o_b-1] == 0:
				self.set_column_to_zero()
				for i in range (10):
					print (self.target_space[i])
				print ("return 2")
				return
			for i in range(10):
				self.target_space[i][self.curr_col] = self.individual_projected_distance(i+1)
		else:
			self.hyperplane_furthest_objects()
			if self.hyperplane_distance(self.o_a, self.o_b) == 0:
				self.set_column_to_zero()
				for i in range (10):
					print (self.target_space[i])
				print ("return 3")
				return
			for i in range(10):
				self.target_space[i][self.curr_col] = self.hyperplane_projected_distance(i+1)
		self.fastmap(k-1)

fastmap = Fastmap()
fastmap.read_data()
fastmap.fastmap(2)


