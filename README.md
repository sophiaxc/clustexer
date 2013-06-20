clustexer
=========

K-Means Cluster Location Data and Generate Convex Hulls CSV/Google Maps HTML Script

This script is used to:
>> cluster data with k-means
>> calculate convex hull
>> display convex hulls as polygons on google maps in HTML with index labels

Data should come in the formats:

    lat, lng, cluster_index

    OR

    lat, lng
    >> In this case, specify the k for clustering with --num-clusters


Example usage to get convex hull polygons to stdout from clustered input:

    python parser.py clustered_data/marin_pts.csv
*Convex Hull Format: neighborhood_index,lat1 lng1; lat2 lng2; lat3 lng3*


Example usage to get convex hulls to stdout from clustered input with label:

    python parser.py clustered_data/marin_pts.csv --cluster-prefix marin
*Convex Hull Format: label, neighborhood_index,lat1 lng1; ...*


Example usage to get convex hulls polygons to stdout from unclustered data:

    python parser.py raw_data/marin_trip_pts.csv --num-clusters 15


Example usage to output convex hulls to html from clustered data with maplatlng:

    python parser.py clustered_data/marin_pts.csv --html marin.html --map-latlng 37.7749, -122.4194


Example usage to get convex hull points from clustered data:

    python parser.py clustered_data/marin_pts.csv --cluster-prefix marin
*Outputs to a file called marin.csv*


Example usage to get convex hulls from unclustered data to html:

    python parser.py raw_data/marin_trip_pts.csv --html marin.html --num-clusters 15


Example usage to get convex hulls from unclustered data to html and save shapes to file:

    python parser.py raw_data/marin_trip_pts.csv --html marin.html --num-clusters 15 --cluster-prefix marin
*Outputs convex hulls to a file called marin.csv*
