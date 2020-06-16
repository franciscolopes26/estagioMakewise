class TrackableObject:
	def __init__(self, objectID, centroid):
		# store the object ID, then initialize a list of centroids
		# using the current centroid
		self.objectID = objectID
		self.centroids = [centroid]

		# initialize a boolean used to indicate if the object has
		# already been counted or not
		self.counted = False

	def is_crossing_line(self,point_a,point_b):
		# this function will check if the line segment form by connection
		# the two last centroids cross the line segment form by the points a and b
		# if centroids size is less that two we don't have a line segment so we will return false
		if len(self.centroids)<2:
			return False

		##Missing code to test crossing line :):):)


		return False


# Small test code

if __name__ == '__main__':

	t = TrackableObject('1',(1,1))
	a = (2,0)
	b = (2,2)

	print("Test TrackableObject centroids with less than two")
	if t.is_crossing_line(a,b) == False:
		print("Test pass")
	else:
		print("Test fail")

	print("Test TrackableObject not crossing the line")
	t.centroids.append((0,1)) # move the other direction away from the line
	if t.is_crossing_line(a,b) == False:
		print("Test pass")
	else:
		print("Test fail")

	print("Test TrackableObject crossing the line")
	t.centroids.append((3, 1))
	if t.is_crossing_line(a,b) == True:
		print("Test pass")
	else:
		print("Test fail")



