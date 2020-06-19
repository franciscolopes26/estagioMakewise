class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Given three colinear points p, q, r, the function checks if


# point q lies on line segment 'pr'
def onSegment(p, q, r):
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False


def orientation(p, q, r):
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Colinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise

    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
    # for details of below formula.

    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if (val > 0):

        # Clockwise orientation
        return 1
    elif (val < 0):

        # Counterclockwise orientation
        return 2
    else:

        # Colinear orientation
        return 0


# The main function that returns true if
# the line segment 'prev_centroid-current_centroid' and 'point_a-point_b' intersect.
def doIntersect(prev_centroid, current_centroid, point_a, point_b):
    # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(prev_centroid, current_centroid, point_a)
    o2 = orientation(prev_centroid, current_centroid, point_b)
    o3 = orientation(point_a, point_b, prev_centroid)
    o4 = orientation(point_a, point_b, current_centroid)

    # General case
    if ((o1 != o2) and (o3 != o4)):
        return True

    # Special Cases

    # prev_centroid , current_centroid and point_a are colinear and point_a lies on segment prev_centroid-current_centroid
    if ((o1 == 0) and onSegment(prev_centroid, point_a, current_centroid)):
        return True

    # prev_centroid , current_centroid and point_b are colinear and point_b lies on segment prev_centroid-current_centroid
    if ((o2 == 0) and onSegment(prev_centroid, point_b, current_centroid)):
        return True

    # point_a , point_b and prev_centroid are colinear and prev_centroid lies on segment point_apoint_b
    if ((o3 == 0) and onSegment(point_a, prev_centroid, point_b)):
        return True

    # point_a , point_b and current_centroid are colinear and current_centroid lies on segment point_apoint_b
    if ((o4 == 0) and onSegment(point_a, current_centroid, point_b)):
        return True

    # If none of the cases
    return False

