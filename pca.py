import sys
import math
import copy
import random

class Clustering:
	def __init__(self, k, list_of_points):
		self.points_space = list_of_points
		self.k = k
		self.clusters = list()
		self.centroids = None
		self.previous_centroids = None
		self.min_distance_from_centroids = sys.maxsize
		self.best_clusters = list()
		self.best_centroids = list()
		self.mu = list()
		self.sigma = list()
		self.pi = list()
		self.responsibilities = list()

	def sum_distance_from_centroids(self):
		sum_distance = 0
		for (cluster, centroid) in zip(self.clusters, self.centroids):
			for point in cluster.points:
				sum_distance += point.sum_of_squares(centroid)
		return sum_distance

	def no_change_in_centroids(self):
		sum_distance = 0
		for (old, new) in zip(self.previous_centroids, self.centroids):
			sum_distance += old.distance_to(new)
		if sum_distance != 0:
			return False
		else:
			return True

	def random_centroids(self):
		centroids = list()
		while len(centroids) < 3:
			point = self.points_space[random.randint(0,len(self.points_space)-1)]
			if (point not in centroids):
				centroids.append(point)
		return centroids

	def assignment(self):
		self.clear_points_from_clusters()
		modified = False
		for point in self.points_space:
			min_distance = 10000
			closest_centroid_index = -1
			for i, centroid in enumerate(self.centroids):
				current_distance = point.distance_to(self.centroids[i])
				if (current_distance < min_distance):
					min_distance = point.distance_to(self.centroids[i])
					closest_centroid_index = i
			self.clusters[closest_centroid_index].add_point(point)
		return

	def clear_points_from_clusters(self):
		for cluster in self.clusters:
			cluster.clear_points()

	def update(self):
		new_centroids = list()
		for cluster in self.clusters:
			total_x = 0
			total_y = 0
			num_points_in_cluster = len(cluster.points)
			for point in cluster.points:
				total_x += point.x
				total_y += point.y
			new_x = total_x / num_points_in_cluster
			new_x = round(new_x, 9)
			new_y = total_y / num_points_in_cluster
			new_y = round(new_y, 9)
			new_centroids.append(Point(new_x, new_y))
		self.previous_centroids = self.centroids
		self.centroids = new_centroids
		return

	def k_means(self):
		no_change = False
		self.centroids = self.random_centroids()
		for i, centroid in enumerate(self.centroids):
			self.clusters.append(Cluster(i, centroid))
		for i in range (0, 1000):	
			while not no_change:
				self.assignment()
				self.update()
				if self.no_change_in_centroids():
					break
			sum_distance_from_centroids = self.sum_distance_from_centroids()
			if  sum_distance_from_centroids < self.min_distance_from_centroids:
				self.min_distance_from_centroids = sum_distance_from_centroids
				self.best_centroids = copy.deepcopy(self.centroids)
				self.best_clusters = copy.deepcopy(self.clusters)
		print ("The best centroids after 1000 runs are: ", self.best_centroids)
		print ("Number of points in clusters: ", len(self.best_clusters[0].points), len(self.best_clusters[1].points), len(self.best_clusters[2].points))
		return

	def initialize_gmm(self):
		# kmeans for initializing
		self.mu = self.best_centroids
		self.sigma = []
		for i, cluster in enumerate(self.best_clusters):
			xx = 0
			xy = 0
			yx = 0
			yy = 0
			Xs = []
			Ys = []
			for point in cluster.points:
				Xs.append(point.x - self.best_centroids[i].x)
				Ys.append(point.y - self.best_centroids[i].y)
			for (x, y) in zip(Xs, Ys):
				xx += x**2
				xy += x*y
				yy += y**2
			yx = xy
			cluster_size = len(cluster.points)
			self.sigma.append([[xx/cluster_size, xy/cluster_size],[yx/cluster_size, yy/cluster_size]])

		self.pi = [len(self.best_clusters[i].points)/150 for i in range(self.k)]

	def gaussian(self, cluster_num, point):
		covariance_matrix = self.sigma[cluster_num]
		a = covariance_matrix[0][0]
		b = covariance_matrix[0][1]
		c = covariance_matrix[1][0]
		d = covariance_matrix[1][1]
		sigma_determinant =  a * d  -  c * b
		sigma_inverse = [[d/ sigma_determinant, -b/sigma_determinant], [-c/sigma_determinant, a/sigma_determinant]]
		x = point.x - self.best_centroids[cluster_num].x
		y = point.y - self.best_centroids[cluster_num].y
		exponent = x*x*sigma_inverse[0][0] + y*x*sigma_inverse[1][0] + x*y*sigma_inverse[0][1] + y*y*sigma_inverse[1][1]

		denominator = ( (2*math.pi) * math.sqrt(sigma_determinant) )
		numerator = math.exp(-1/2* (exponent) )
		return (numerator / denominator)

	def e_step(self):
		self.responsibilities = []
		for point in self.points_space:
			denominator = 0
			point_responsibility = []
			for i in range (k):
				denominator += self.pi[i] * self.gaussian(i, point)

			for i in range (k):
				point_responsibility.append(self.pi[i] * self.gaussian(i, point)/ denominator)
			self.responsibilities.append(point_responsibility)
			temp = 0
		for i in range(150):
			for j in range (3):
				temp += self.responsibilities[i][j]
		return

	def m_step_covar_helper(self, i, pi):
		xx = 0
		xy = 0
		yx = 0
		yy = 0
		Xs = []
		Ys = []
		for (j, point) in enumerate(self.best_clusters[i].points):
			point_responsibility = self.responsibilities[j][i]
			Xs.append(point_responsibility*(point.x - self.best_centroids[i].x))
			Ys.append(point_responsibility*(point.y - self.best_centroids[i].y))
		for (x, y) in zip(Xs, Ys):
			xx += x**2
			xy += x*y
			yy += y**2
			yx += y*x
		return ([[xx/pi, xy/pi],[yx/pi, yy/pi]])

	def m_step(self):
		self.mu = []
		self.sigma = []
		self.pi = []
		for i in range (k):
			mu = [0,0]
			pi = 0
			for (j, point) in enumerate(self.points_space):
				point_responsibility = self.responsibilities[j][i]
				mu[0] += point_responsibility*point.x
				mu[1] += point_responsibility*point.y
				pi += point_responsibility
				#print (i, j)
				#print (pi)
			mu[0] /= pi
			mu[1] /= pi
			self.mu.append(mu)
			self.sigma.append(self.m_step_covar_helper(i, pi))
			self.pi.append(pi/150)

	def gmm(self):
		self.initialize_gmm()
		self.e_step()
		self.m_step()
		print ("Gaussian 1: mean, amplitude, covariance", self.mu[0], self.pi[0], self.sigma[0])
		print ("Gaussian 2: mean, amplitude, covariance", self.mu[1], self.pi[1], self.sigma[1])
		print ("Gaussian 3: mean, amplitude, covariance", self.mu[2], self.pi[2], self.sigma[2])


class Cluster:
	def __init__(self, id, centroid):
		self.id = id
		self.points = list()
		self.centroid = centroid
	
	def add_point(self, point):
		self.points.append(point)

	def clear_points(self):
		self.points.clear()

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.cluster = None

	def __repr__(self):
		return str(self.x) + " " + str(self.y)

	def distance_to(self, another_point):
		return math.sqrt( (another_point.x - self.x)**2 + (another_point.y - self.y)**2 )

	def sum_of_squares(self, another_point):
		return (another_point.x - self.x)**2 + (another_point.y - self.y)**2

# reads a file and returns a list of points
def read_data():
	list_of_points = []
	with open('clusters.txt', 'r') as rawdata:
		lines = rawdata.readlines()
		for line in lines:
			if line != '\n':
				line.rstrip()
				raw_point = line.split(',')
				int_point = Point(float(raw_point[0]), float(raw_point[1]))
				list_of_points.append(int_point)
	return list_of_points

k = 3
list_of_points = read_data()
clustering = Clustering(k, list_of_points)
clustering.k_means()
clustering.gmm()
