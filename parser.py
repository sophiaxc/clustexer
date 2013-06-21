import argparse
import numpy

from numpy import array
from scipy.cluster.vq import kmeans,vq
from collections import defaultdict
from pyhull.convex_hull import ConvexHull
from jinja2 import Environment, FileSystemLoader

"""
Data should come in the formats:

    lat, lng, cluster_index

    OR

    lat, lng
    >> In this case, specify the k for clustering with --num-clusters

Example usage to get convex hull polygons to stdout from clustered input:
python parser.py clustered_data/marin_pts.csv
    >> Convext Hull Format: neighborhood_index,lat1 lng1; lat2 lng2; lat3 lng3

Example usage to get convex hulls to stdout from clustered input with label:
python parser.py clustered_data/marin_pts.csv --cluster-prefix marin
    >> Convext Hull Format: label, neighborhood_index,lat1 lng1; ...

Example usage to get convex hulls polygons to stdout from unclustered data
python parser.py raw_data/marin_trip_pts.csv --num-clusters 15

Example usage to output convex hulls to html from clustered data:
python parser.py clustered_data/marin_pts.csv --html marin.html

Example usage to get convex hull points from clustered data:
python parser.py clustered_data/marin_pts.csv --cluster-prefix marin
    >> Outputs to a file called marin.csv

Example usage to get convex hulls from unclustered data to html
python parser.py raw_data/marin_trip_pts.csv --html marin.html --num-clusters 15

Example usage to get convex hulls from unclustered data to html and save shapes to file
python parser.py raw_data/marin_trip_pts.csv --html marin.html
        --num-clusters 15 --cluster-prefix marin
    >> Outputs convex hulls to a file called marin.csv
"""

def parse_file(filename, output_html=None, cluster_prefix=None,
               num_clusters=None):
    """ Parses a file for clustering/display.

    Given a filename in the format of lat, lng, neighborhood id,
    generate the convex hull polygon for each neighborhood.
    """
    cluster_points = {}
    if num_clusters is None:
        cluster_points = read_clustered_data(filename)
    else:
        cluster_points = read_unclustered_data(filename, num_clusters)

    # Generate the convex hulls mapped to their cluster id
    convex_hulls = dict((id, get_convex_hull_polygon(points))
            for id, points in cluster_points.iteritems())

    if output_html is not None:
        f = open(output_html, 'w')
        env = Environment(loader=FileSystemLoader('./'))
        template = env.get_template('_base.html')
        polygon_centers = dict((id, get_polygon_center(polygon))
                for id, polygon in convex_hulls.iteritems())
        f.write(template.render(
                convex_hulls=convex_hulls,
                polygon_centers=polygon_centers,
                map_bounds=get_map_bounds(convex_hulls)))
        f.close()

    [output_formatted_polygon(id, polygon, cluster_prefix)
            for id, polygon in convex_hulls.iteritems()]

def get_map_bounds(convex_hulls):
    """ Return dictionary of map bounding box coordinates.

    Using the points of all the convex hulls, calculates the bounding box
    for the map to display the convex hulls.
    """
    all_points = []
    for id, polygon in convex_hulls.iteritems():
        all_points.extend(polygon)
    lats = [point[0] for point in all_points]
    lngs = [point[1] for point in all_points]

    south, north = min(lats), max(lats)
    west, east = min(lngs), max(lngs)

    # Flip east/west if the bounding doesn't contain polygons.
    # Check if each point is within the west/east bounds.
    if not (all([west <= lng <= east for lng in lngs])):
        east, west = west, east

    return {"SW" : [south, west], "NE" : [north, east]}

def read_unclustered_data(filename, num_clusters):
    """ Return dictionary of cluster id to array of points.

    Given a filename in the format of lat, lng
    generate k clusters based on arguments. Outputs a dictionary with
    the cluster id as the key mapped to a list of lat, lng pts
    """
    request_points = []
    f = open(filename, 'rb')
    f.next() # Skip the header row
    for line in f:
        lat, lng = line.split(",")
        request_points.append([float(lat), float(lng)])
    request_points = array(request_points)

    # computing K-Means with K = num_clusters
    centroids,_ = kmeans(request_points, int(num_clusters))
    # assign each sample to a cluster
    idx,_ = vq(request_points,centroids)

    # map cluster lat, lng to cluster index
    cluster_points = defaultdict(list)
    for i in xrange(len(request_points)):
        lat, lng = request_points[i]
        cluster_points[idx[i]].append([lat, lng])
    return cluster_points

def read_clustered_data(filename):
    """ Return dictionary of cluster id to array of points.

    Given a filename in the format of lat, lng, cluster_id
    Outputs a dictionary with the cluster id as the key mapped to
    a list of lat, lng pts
    """
    cluster_points = defaultdict(list)
    f = open(filename, 'rb')
    f.next() # Skip the header row
    for line in f:
        lat, lng, id = line.split(",")
        cluster_points[int(id)].append([float(lat), float(lng)])
    return cluster_points

def output_formatted_polygon(id, polygon_points, prefix=None):
    """ Writes out formatted polygons to stdout or file.

    If prefix is defined, outputs row as
    prefix,neighborhood_n,x1 y1;x2 y2;x3 y3
    """

    formatted_points = ";".join(["%s %s" % tuple(pt) for pt in polygon_points])
    output = ["neighborhood_%s" % id, formatted_points]
    if prefix:
        output.insert(0, prefix)
        f = open("%s.csv" % prefix, 'a')
        f.write(",".join(output))
        f.write("\n")
        f.close()
    else:
        print ",".join(output)

def get_polygon_center(points):
    """ Returns a tuple representing a polygon center.

    Get a polygon's "center" by averaging the x/y
    """
    return (numpy.mean([point[0] for point in points]),
            numpy.mean([point[1] for point in points]))

def get_convex_hull_polygon(points):
    """ Returns an array of points.

    Given a set of points, generate the convex hull as a polygon.
    """
    hull = ConvexHull(points)
    # break it out into a dictionary of vertex to its neighbor vertex.
    vertices_dict = dict((vertex[0], vertex[1]) for vertex in hull.vertices)
    ordered_vertices = follow_vertices(hull.vertices[0][0], vertices_dict)
    polygon_points = [hull.points[index] for index in ordered_vertices]
    return polygon_points

def follow_vertices(start_vertex, vertices_dict):
    """ Returns an array of vertices.

    Follow the start vertex to generate the vertices in order, given
    a dictionary with the key as a vertex and the value as its neighbor vertex.
    """
    vertices = [start_vertex]
    next_vertex = vertices_dict[start_vertex]
    while (next_vertex != start_vertex):
        vertices.append(next_vertex)
        next_vertex = vertices_dict[next_vertex]
    vertices.append(start_vertex)
    return vertices

# Paaaarsing!
parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('--html',
        help="If specified, outputs html representation of clusters to filename.")
parser.add_argument('--cluster-prefix',
        help="If specified, cluster prefix outputs polygons to a file of")
parser.add_argument('--num-clusters', type=int,
        help="If specified, k means clusters are computed from the input file.")
args = parser.parse_args()
parse_file(args.filename, args.html, args.cluster_prefix, args.num_clusters)
