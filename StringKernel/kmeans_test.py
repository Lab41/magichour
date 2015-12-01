from sklearn.preprocessing import scale
from sklearn.cluster import KMeans

from utility import *
from string_kernel import *

def test(dirpath, k):
    files = get_files(dirpath)
    lines = []
    for f in files:
        lines.extend(get_lines(f))
    
    feature_list, data = ss_kernel(lines)
    scaled = scale(data)

    kmeans = KMeans(n_clusters=k)
    kmeans.fit(scaled)
    return zip(kmeans.labels_, lines)
    
