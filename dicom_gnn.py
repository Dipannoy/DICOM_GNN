# -*- coding: utf-8 -*-
"""DICOM_GNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ppU34894bRH3VT938OH5WyuJjTzScqgh
"""

from google.colab import drive
drive.mount('/gdrive')

pip install open3d pydicom opencv-python

!apt-get install -y graphviz libgraphviz-dev libcgraph6

!pip install git+https://github.com/danielegrattarola/spektral

import open3d as o3d
import numpy as np
import cv2
import pydicom
import os
import matplotlib.pyplot as plt
from glob import glob
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
##import skimage
import scipy.ndimage
import imageio
from skimage import morphology
from skimage import measure
from skimage.transform import resize
from sklearn.cluster import KMeans
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.tools import FigureFactory as FF
from plotly.graph_objs import *
##init_notebook_mode(connected=True)

import scipy.sparse as sp
import tensorflow as tf
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.metrics import categorical_accuracy
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

from spektral.data import Dataset, DisjointLoader, Graph
from spektral.layers import GCSConv, GlobalAvgPool, AGNNConv, APPNPConv,ARMAConv
from spektral.layers.pooling import TopKPool
from spektral.transforms.normalize_adj import NormalizeAdj

data_path = "/gdrive/My Drive/BD066"
# output_path = working_path = "F:\SelfContent\DeepLearningWork\ImageProcessing"
img = os.path.join("/gdrive/My Drive/BD066","file")

def load_scan(path):
    slices = [pydicom.read_file(path + '/' + s) for s in os.listdir(path)]
    # slices = []
    # files = os.listdir(path)
    # fileLength = len(files) // 2
    # for i in range(fileLength) :
    #     slc = pydicom.read_file(path + '/' + files[i])
    #     slices.append(slc)
        


    slices.sort(key = lambda x: int(x.InstanceNumber))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
        
    for s in slices:
        s.SliceThickness = slice_thickness
        
    return slices


def get_pixels_hu(scans):
    print(len(scans[0]))
    #print(scans[0].pixel_array)
    #out_tpl = np.nonzero(scans[0].pixel_array)
    out_arr = scans[0].pixel_array[np.nonzero(scans[0].pixel_array)]
    print(len(out_arr))
    #image = np.stack([scans[s].pixel_array for s in range(1, len(scans)//2)])
    image = np.stack([s.pixel_array  for s in scans])
    # Convert to int16 (from sometimes int16), 
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)
    

    # Set outside-of-scan pixels to 1
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0
    # image = image[image == 30]
    
    # Convert to Hounsfield units (HU)
    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope
    
    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)
        
    image += np.int16(intercept)
    # image[image != 0] = 0
    # print(len(image))
    # print(image)
    # image2 = image[(image >= 500) & (image <= 3000)]

    # --------------------------------------------------
    image[image < 100] = 0
    # image[image < 900] = -1000


    
    

    
    return np.array(image, dtype=np.int16)
id=0
patient = load_scan(data_path)
imgs = get_pixels_hu(patient)
# print(len(imgs))
# print ("Shape before resampling\t", imgs.shape)

print(len(imgs))

cropImageArray = []
resizeImageArray = []
for i in range(350):
  cropImage = imgs[i][120:350,100:250]
  res = cv2.resize(cropImage, dsize=(10, 10), interpolation=cv2.INTER_CUBIC)
  cropImageArray.append(cropImage)
  resizeImageArray.append(res)

plt.imshow(cropImageArray[40])
plt.show()

import scipy.ndimage
from skimage.segmentation import slic
from scipy.spatial.distance import cdist
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
from skimage import io

def sample_stack(stack, rows=2, cols=2, start_with=1, show_every=1):
    fig,ax = plt.subplots(rows,cols,figsize=[12,12])
    for i in range(rows*cols):

        ind = start_with + i*show_every
   
        ax[int(i/rows),int(i % rows)].set_title('slice %d' % ind)
        ax[int(i/rows),int(i % rows)].imshow(stack[ind])
        ax[int(i/rows),int(i % rows)].axis('off')
    plt.show()

sample_stack(cropImageArray)

print(cropImageArray)

import numpy as np
import cv2

img = 

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

blurred = cv2.medianBlur(gray, 25) #cv2.bilateralFilter(gray,10,50,50)

minDist = 100
param1 = 30 #500
param2 = 50 #200 #smaller value-> more false circles
minRadius = 5
maxRadius = 100 #10

# docstring of HoughCircles: HoughCircles(image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]]) -> circles
circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)

# Show result for testing:
cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

import matplotlib.pyplot as plt
import numpy as np

from skimage.data import astronaut
from skimage.color import rgb2gray
from skimage.filters import sobel
from skimage.segmentation import felzenszwalb, slic, quickshift, watershed
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float

# img = img_as_float(imgs[0])
img = cropImageArray[40]
segments_fz = felzenszwalb(img, scale=100, sigma=0.5, min_size=50)
# segments_slic = slic(img,n_segments=500,compactness=0.01, enforce_connectivity=True)
segments_slic = slic(img, n_segments=100,compactness=0.01, multichannel=False)

# segments_quick = quickshift(img, kernel_size=3, max_dist=6, ratio=0.5)
gradient = sobel(rgb2gray(img))
segments_watershed = watershed(gradient, markers=200, compactness=0.001)

print(f"Felzenszwalb number of segments: {len(np.unique(segments_fz))}")
print(f"SLIC number of segments: {len(np.unique(segments_slic))}")
# print(f"Quickshift number of segments: {len(np.unique(segments_quick))}")

fig, ax = plt.subplots(2, 2, figsize=(10, 10), sharex=True, sharey=True)

ax[0, 0].imshow(mark_boundaries(img, segments_fz))
ax[0, 0].set_title("Felzenszwalbs's method")
ax[0, 1].imshow(mark_boundaries(img, segments_slic))
ax[0, 1].set_title('SLIC')
# ax[1, 0].imshow(mark_boundaries(img, segments_quick))
# ax[1, 0].set_title('Quickshift')
ax[1, 1].imshow(mark_boundaries(img, segments_watershed))
ax[1, 1].set_title('Compact watershed')

for a in ax.ravel():
    a.set_axis_off()

plt.tight_layout()
plt.show()

print(segments_watershed)

a = np.array(cropArray[0])
unique, counts = np.unique(a, return_counts=True)
print(dict(zip(unique, counts)))

plt.imshow(noiseFreeImage[52])
plt.show()

import copy
from skimage.segmentation import felzenszwalb, slic, quickshift, watershed

for i in cropImageArray[20:30]:
  plt.imshow(i)
  plt.show()

imgg = cropImageArray[22]
# imgg = modImage
segments_fz2 = felzenszwalb(imgg, scale=30, sigma=0.5, min_size=50)
sp_indices = np.unique(segments_fz2)
cropArray = []
indx = 0


for seg in sp_indices:
    mask = segments_fz2 == seg
    shp = np.array(segments_fz2.shape)
    modImage = copy.deepcopy(imgg)
    for i in range(shp[0]):
      for j in range(shp[1]):
        if mask[i][j] == False:
          modImage[i][j] = 0
    plt.imshow(modImage)
    plt.show()

gradient = sobel(rgb2gray(modImage))
segments_watershed = watershed(gradient, markers=400, compactness=0.002)
plt.imshow(mark_boundaries(modImage, segments_watershed))
plt.show()

noiseFreeImage = []
count = 280
for i in cropImageArray[40:41]:
  # if count == 298:
  #   sig = 0.8
  # else:
  #   sig = 0.5
  segments_fz = felzenszwalb(i, scale=100, sigma=0.5, min_size=50)

  # segments_fz = felzenszwalb(i, scale=30, sigma=1, min_size=50)
  a = np.array(segments_fz)
  unique, counts = np.unique(a, return_counts=True)
  dctn = dict(zip(unique, counts))
  sort_orders = sorted(dctn.items(), key=lambda x: x[1], reverse=True)
  keyArray = list(dict(sort_orders).keys())
  if keyArray[0] == 0 : 
    seg = keyArray[1]
  else :
    seg = keyArray[0]
  mask = segments_fz == seg
  shp = np.array(segments_fz.shape)
  modImage = copy.deepcopy(i)
  for i in range(shp[0]):
    for j in range(shp[1]):
      if mask[i][j] == False:
        modImage[i][j] = 0
  print(count)
  plt.imshow(modImage)
  plt.show()
  count = count + 1
  noiseFreeImage.append(modImage)

refArray = []
refArray2 = []
for i in range(0,340):
  if i % 2 == 0:
    refArray.append(cropImageArray[i])
  else :
    refArray.append(cropImageArray[i-1])
  # plt.imshow(cropImageArray[i])
  # plt.show()

pip install trimesh

count = 300
newRef = []
for i in refArray[0:300]:
  newRef.append(i)

for i in refArray[300:320]:
  # segments_fz = felzenszwalb(i, scale=100, sigma=0.5, min_size=50)

  segments_fz = felzenszwalb(i, scale=50, sigma=0.2, min_size=50)
  a = np.array(segments_fz)
  unique, counts = np.unique(a, return_counts=True)
  dctn = dict(zip(unique, counts))
  sort_orders = sorted(dctn.items(), key=lambda x: x[1], reverse=True)
  keyArray = list(dict(sort_orders).keys())
  if keyArray[0] == 0 : 
    seg = keyArray[1]
  else :
    seg = keyArray[0]
  mask = segments_fz == seg
  shp = np.array(segments_fz.shape)
  modImage = copy.deepcopy(i)
  for i in range(shp[0]):
    for j in range(shp[1]):
      if mask[i][j] == False:
        modImage[i][j] = 0
  newRef.append(modImage)
  print(count)
  plt.imshow(modImage)
  plt.show()
  count = count + 1

for i in refArray[300:320]:
  plt.imshow(i)
  plt.show()

verts, faces, norm, val = measure.marching_cubes_lewiner(np.array(refArray[20:325]),300, step_size=1, allow_degenerate=True) 
x,y,z = zip(*verts)
print(len(verts))

import trimesh
# mesh = trimesh.load_mesh('mesh.stl')
mesh = trimesh.Trimesh(vertices=verts,
                       faces=faces
                       )
mesh.show()

colormap=['rgb(236, 236, 212)','rgb(236, 236, 212)']
fig = FF.create_trisurf(x=x,
                       y=y, 
                       z=z, 
                       plot_edges=False,
                       colormap=colormap,
                       simplices=faces,
                       edges_color = 'rgb(0, 0, 0)', 
                       backgroundcolor='rgb(64, 64, 64)',
                       title="Interactive Visualization")
fig.update_layout(
    autosize=True,
    height=800,)
iplot(fig)

plt.imshow(modImage)
plt.show()

# The number (n_segments) of superpixels returned by SLIC is usually smaller than requested, so we request more
superpixels = slic(img, n_segments=95, compactness=0.25, multichannel=False)
sp_indices = np.unique(superpixels)
n_sp = len(sp_indices)  # should be 74 with these parameters of slic

sp_intensity = np.zeros((n_sp, 1), np.float32)
sp_coord = np.zeros((n_sp, 2), np.float32)  # row, col
for seg in sp_indices:
    mask = superpixels == seg
    sp_intensity[seg] = np.mean(img[mask])
    sp_coord[seg] = np.array(scipy.ndimage.measurements.center_of_mass(mask))

# The model is invariant to the order of nodes in a graph
# We can shuffle nodes and obtain exactly the same results
ind = np.random.permutation(n_sp)
sp_coord = sp_coord[ind]
sp_intensity = sp_intensity[ind]

import torch
from torchvision import datasets
# data = datasets.MNIST('./data', train=False, download=True)
# images = (data.test_data.numpy() / 255.)


import numpy as np
imgArray = []
# # img = images[0].astype(np.double)  # 28x28 MNIST image
# # img2 = images[1].astype(np.double)
# img = imgs[0]
# img2 = imgs[1]
# print(len(imgs))
# for i in range(100):
#   imgArray.append(imgs[i])
# # imgArray.append(img)
# # imgArray.append(img2)
# # print(len(im))
# uniquePixel = np.unique(imgArray)
# print(len(uniquePixel))
imgArray = cropImageArray

print(cropImageArray)

# print((images[0]))
# print((img2.shape))
shape = np.ones((230,300,100))
# print(shape.shape)
print(shape.shape)

import numpy as np
import scipy.ndimage
from skimage.segmentation import slic
from scipy.spatial.distance import cdist

import scipy.ndimage
from skimage.segmentation import slic
from scipy.spatial.distance import cdist

# The number (n_segments) of superpixels returned by SLIC is usually smaller than requested, so we request more
# superpixels = slic(np.array(imgArray), n_segments=1000,compactness=0.01, multichannel=False)
superpixels = slic(imgArray, n_segments=1000,compactness=0.01, multichannel=False)


# print(superpixels)
# superpixels = slic(np.array(imgArray),n_segments=500,compactness=0.01, enforce_connectivity=True)
sp_indices = np.unique(superpixels)
# print(sp_indices)
n_sp = len(sp_indices)  # should be 74 with these parameters of slic
# print(n_sp)

sp_intensity = np.zeros((n_sp, 1), np.float32)

sp_coord = np.zeros((n_sp, 3), np.float32)  # row, col
# print(sp_coord)
# print(superpixels.shape)

for seg in sp_indices:
    mask = superpixels == seg
    # print(seg)
    sp_intensity[seg] = np.max(np.array(imgArray)[mask])
    # print(sp_intensity[seg])
    sp_coord[seg] = (scipy.ndimage.measurements.center_of_mass(mask))
    # sp_coord[seg] = scipy.ndimage.measurements.center_of_mass(np.array(mask))

    # print(sp_coord[seg])
    
#     sp_coord[seg] = scipy.ndimage.measurements.center_of_mass(mask)

# # The model is invariant to the order of nodes in a graph
# # We can shuffle nodes and obtain exactly the same results
ind = np.random.permutation(n_sp)
sp_coord = sp_coord[ind]
sp_intensity = sp_intensity[ind]
# print(sp_intensity.shape)

print(cropImageArray[0][0][0])

allPixel = 10 * 10 * 10
region = 0
sp_intensity_test = np.zeros((allPixel, 1), np.float32)
sp_coord_test = np.zeros((allPixel, 3), np.int) 
# superPixelArray  = np.ones((100,230,300),int)
for i in range(10):
  for j in range(10):
    for k in range(10):
        # superPixelArray[i][j][k] = region

        sp_intensity_test[region] = resizeImageArray[i][j][k]
        sp_coord_test[region] = (i,j,k)
        region = region + 1

print(sp_coord_test)

print((sp_coord_test))

# print(np.array(sp_intensity,int))
print(imgArray[0].shape)
print(sp_intensity)

maskTest = [True,False]
arr = np.array([1, 2, 10, 4, 5, 10, 7, 8, 9, 10, 11, 12])

newarr = arr.reshape(2, 3, 2)
print(newarr)
maskk = newarr == 10
print(maskk)
print(scipy.ndimage.measurements.center_of_mass(maskk))
# print(np.mean(np.array(newarr)[maskk]))
# print(newarr[maskTest])

shapeArray = [512,512,2]
print(np.array(shapeArray).shape)

from skimage import measure

sp_coord_test = np.ones((30000, 3), np.int)

# sp_coord = sp_coord / shape.shape
dist = cdist(sp_coord_test, sp_coord_test)  # distance between all pairs of nodes
sigma = 0.1 * np.pi  # width of a Guassian
# A_Test = np.exp(- dist / sigma ** 2)  # transform distance to spatial closeness
A_Test = dist
A_Test[np.diag_indices_from(A_Test)] = 0  # remove self-loops
# A = torch.from_numpy(A).float().unsqueeze(0)
A_Test= sp.csr_matrix(A_Test)
print(A_Test)
# A = torch.from_numpy(A).float().unsqueeze(0)
# print(A)
# verts, faces, norm, val = measure.marching_cubes_lewiner(A, -300,step_size=5, allow_degenerate=True)

from plotly.tools import FigureFactory as FF

X_cord = []
Y_cord = []
Z_cord = []
f = open("graph.ply", "a")


#open and read the file after the appending:


for c in sp_coord:
  print(c[1])
  # f.write(str(c[0]) + " " + str(c[1]) + " " + str(c[2]))
  # f.write("\n")
f.close()
# f = open("demofile2.txt", "r")
# print(f.read())

# fig = go.Figure(data=[go.Mesh3d(x=X_cord, y=Y_cord, z=Z_cord, color='lightpink', opacity=0.50)])
# fig.show()

coords = np.array(sp_coord)
vertices = []
x_mod = []
y_mod = []
z_mod = []
indx = 0
for v in coords:
  vertices.append([])
  vertices[indx].append(v[0])
  vertices[indx].append(v[1])
  vertices[indx].append(v[2])
  x_mod.append(v[0])
  y_mod.append(v[1])
  z_mod.append(v[2])
  indx= indx + 1
x_mod = tuple(x_mod)
y_mod = tuple(y_mod)
z_mod = tuple(z_mod)
# print(vertices)

class Edge:
  def __init__(self, node1, node2, weight):
    self.node1 = node1
    self.node2 = node2
    self.weight = weight

print(imgArray)

from itertools import combinations
import math

class MyDatasetTest(Dataset):
    """
    A dataset of random colored graphs.
    The task is to classify each graph with the color which occurs the most in
    its nodes.
    The graphs have `n_colors` colors, of at least `n_min` and at most `n_max`
    nodes connected with probability `p`.
    """

    def __init__(self, n_samples, n_colors=3, n_min=10, n_max=100, p=0.1, **kwargs):
        self.n_samples = n_samples
        self.n_colors = n_colors
        self.n_min = n_min
        self.n_max = n_max
        self.p = p
        super().__init__(**kwargs)

    def read(self):
        def make_graph():
            n = 10000
            colors = np.random.randint(0, self.n_colors, size=n)

            # Node features
            x = sp_intensity_test

            # Edges
            a= A_Test

            # Labels
            y = np.zeros((self.n_colors,))
            color_counts = x.sum(0)
            y[np.argmax(color_counts)] = 1

            return Graph(x=x, a=a, y=y)

        # We must return a list of Graph objects
        return [make_graph() for _ in range(self.n_samples)]

print(len(imgArray))

"""
This example shows how to define your own dataset and use it to train a
non-trivial GNN with message-passing and pooling layers.
The script also shows how to implement fast training and evaluation functions
in disjoint mode, with early stopping and accuracy monitoring.

The dataset that we create is a simple synthetic task in which we have random
graphs with randomly-colored nodes. The goal is to classify each graph with the
color that occurs the most on its nodes. For example, given a graph with 2
colors and 3 nodes:

x = [[1, 0],
     [1, 0],
     [0, 1]],

the corresponding target will be [1, 0].
"""

import numpy as np
import scipy.sparse as sp
import tensorflow as tf
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.metrics import categorical_accuracy
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

from spektral.data import Dataset, DisjointLoader, Graph
from spektral.data import SingleLoader
from spektral.layers import GCSConv, GlobalAvgPool
from spektral.layers.pooling import TopKPool
from spektral.transforms.normalize_adj import NormalizeAdj

################################################################################
# PARAMETERS
################################################################################
learning_rate = 1e-2  # Learning rate
epochs = 500  # Number of training epochs
es_patience = 10  # Patience for early stopping
batch_size = 5  # Batch size
# AdjMatrix = A
# FeatureVector = sp_intensity
tranImages = imgArray[0:10]

y_test = np.zeros((3,))
color_counts = sp_intensity_test.sum(0)
y_test[np.argmax(color_counts)] = 1
# print(FeatureVector)
################################################################################
# LOAD DATA
################################################################################
class MyDataset(Dataset):
    """
    A dataset of random colored graphs.
    The task is to classify each graph with the color which occurs the most in
    its nodes.
    The graphs have `n_colors` colors, of at least `n_min` and at most `n_max`
    nodes connected with probability `p`.
    """

    def __init__(self, n_samples,n_slices,n_colors = 3, p=0.1, **kwargs):
        self.n_samples = n_samples
        self.n_colors = n_colors
        self.n_slices = n_slices
        self.p = p
        super().__init__(**kwargs)

    def read(self):
        def make_graph(imageGrid):
            n = 10
            colors = np.random.randint(0, self.n_colors, size=n)

            # Node features
            # x = np.zeros((n, self.n_colors))
            # x[np.arange(n), colors] = 1
            feat, coord = make_feature(imageGrid)
            x = feat
            # Edges
            # a = np.random.rand(n, n) <= self.p
            # a = np.maximum(a, a.T).astype(int)
            # a = sp.csr_matrix(a)
            a= make_adjMatrix(coord)

            # Labels
            y = np.zeros((self.n_colors,))
            color_counts = x.sum(0)
            y[np.argmax(color_counts)] = 1

            return Graph(x=x, a=a, y=y)

        def make_feature(imageGrid):
            superpixels = slic(imageGrid, n_segments=1000,compactness=0.01, multichannel=False)

            sp_indices = np.unique(superpixels)
       
            n_sp = len(sp_indices)  # should be 74 with these parameters of slic

            sp_intensity = np.zeros((n_sp, 1), np.float32)

            sp_coord = np.zeros((n_sp, 2), np.float32)  # row, col


            for seg in sp_indices:
                mask = superpixels == seg
                sp_intensity[seg] = np.max(np.array(imageGrid)[mask])
                sp_coord[seg] = (scipy.ndimage.measurements.center_of_mass(mask))

            return sp_intensity, sp_coord

        def make_adjMatrix(coordinate):
            dist = cdist(coordinate, coordinate)  # distance between all pairs of nodes
            # sigma = 0.1 * np.pi  # width of a Guassian
            # A = np.exp(- dist / sigma ** 2)  # transform distance to spatial closeness
            A = dist
            A[np.diag_indices_from(A)] = 0  # remove self-loops
            A = sp.csr_matrix(A)
            return A


        # We must return a list of Graph objects
        # return [make_graph() for _ in range(self.n_samples)]
        for i in self.n_slices :
          return [make_graph(i)]


dataset = MyDataset(10, tranImages,transforms=NormalizeAdj())
test_dataset = MyDatasetTest(1,transforms=NormalizeAdj())
# print(np.array(dataset[0].a.shape))
# Parameters
F = dataset.n_node_features  # Dimension of node features
# n_out = dataset.n_labels  # Dimension of the target

# Train/valid/test split
# idxs = np.random.permutation(len(dataset))
# split_va, split_te = int(0.8 * len(dataset)), int(0.9 * len(dataset))
# idx_tr, idx_va, idx_te = np.split(idxs, [split_va, split_te])
# dataset_tr = dataset[idx_tr]
# dataset_va = dataset[idx_va]
# dataset_te = dataset[idx_te]
# # print(idx_te)
# print(np.array(dataset_te[0].x))

loader_tr = DisjointLoader(dataset, batch_size=batch_size, epochs=epochs)
# loader_tr = DisjointLoader(dataset, batch_size=batch_size)

# loader_va = DisjointLoader(dataset_va, batch_size=batch_size)
loader_te = DisjointLoader(test_dataset, batch_size=batch_size)

# print(loader_tr)
# for elem in loader_tr:
#     print(elem)
# loader_tr = SingleLoader(dataset)
# loader_te = SingleLoader(dataset)

# loader_tr = loader_tr.load()
################################################################################
# BUILD (unnecessarily big) MODEL
################################################################################
X_in = Input(shape=(F,), name="X_in")
A_in = Input(shape=(None,), sparse=True)
I_in = Input(shape=(), name="segment_ids_in", dtype=tf.int32)

# X_1 = GCSConv(32, activation="relu")([X_in, A_in])
X_1 = AGNNConv(trainable=False, aggregate='sum', activation="relu")([X_in, A_in])
# X_1, A_1, I_1 = TopKPool(ratio=1)([X_1, A_in, I_in])
X_2 = AGNNConv(trainable=False, aggregate='sum', activation="relu")([X_1, A_in])
# X_2, A_2, I_2 = TopKPool(ratio=)([X_2, A_1, I_1])
X_3 = AGNNConv(trainable=False, aggregate='sum', activation="relu")([X_2, A_in])
# X_3, A_3, I_3 = TopKPool(ratio=0.5)([X_3, A_2, I_2])
# X_3 = GlobalAvgPool()([X_3, I_2])
# output = Dense(n_out, activation="softmax")(X_3)
output = X_3
# Build model
model = Model(inputs=[X_in, A_in,I_in], outputs= output)
opt = Adam(lr=learning_rate)
loss_fn = CategoricalCrossentropy()


################################################################################
# FIT MODEL
################################################################################


# model(DisjointLoader(dataset), training=True)
# best_weights = model.get_weights()

@tf.function(input_signature=loader_tr.tf_signature(), experimental_relax_shapes=True)
def train_step(inputs, target):
    with tf.GradientTape() as tape:
        predictions = model(inputs, training=True)
        
        # loss = loss_fn(target, predictions)
        # loss += sum(model.losses)
        loss = .2
    # gradients = tape.gradient(loss, model.trainable_variables)
    # opt.apply_gradients(zip(gradients, model.trainable_variables))
    # acc = tf.reduce_mean(categorical_accuracy(target, predictions))
    acc = .6
    return loss, acc
i = 0;
for batch in loader_tr:
    outs = train_step(*batch)
    best_weights = model.get_weights()
    # print(best_weights)


def evaluate(loader,task):
    output = []
    step = 0
    while step < loader.steps_per_epoch:
        step += 1
        inputs, target = loader.__next__()
        # inputs, target = loader
        pred = model(inputs, training=False)
        # if task == "test":
        #   print(pred)
        # outs = (
        #     loss_fn(target, pred),
        #     tf.reduce_mean(categorical_accuracy(target, pred)),
        # )
        # output.append(outs)
    return pred


# print("Fitting model")
# current_batch = epoch = model_loss = model_acc = 0
# best_val_loss = np.inf
# best_weights = None
# patience = es_patience

# for batch in loader_tr:
#     outs = train_step(*batch)

#     model_loss += outs[0]
#     model_acc += outs[1]
#     current_batch += 1
#     if current_batch == loader_tr.steps_per_epoch:
#         model_loss /= loader_tr.steps_per_epoch
#         model_acc /= loader_tr.steps_per_epoch
#         epoch += 1

#         ## Compute validation loss and accuracy
#         # val_loss, val_acc = evaluate(loader_va,"valid")
#         # print(
#         #     "Ep. {} - Loss: {:.2f} - Acc: {:.2f} - Val loss: {:.2f} - Val acc: {:.2f}".format(
#         #         epoch, model_loss, model_acc, val_loss, val_acc
#         #     )
#         # )

#         ## Check if loss improved for early stopping
#         # if val_loss < best_val_loss:
#         #     best_val_loss = val_loss
#         #     patience = es_patience
#         #     print("New best val_loss {:.3f}".format(val_loss))
#         #     best_weights = model.get_weights()
#         # else:
#         #     patience -= 1
#         #     if patience == 0:
#         #         print("Early stopping (best val_loss: {})".format(best_val_loss))
#         #         break
#         model_loss = 0
#         model_acc = 0
#         current_batch = 0

# ################################################################################
# # EVALUATE MODEL
# ################################################################################
print("Testing model")
model.set_weights(best_weights)  # Load best model
# test_loss, test_acc = evaluate(loader_te,"test")
predModel = evaluate(loader_te,"test")
# print(np.array(predModel,int))
# batch2 = predModel.__next__()
# inputs2, target2 = predModel
# x, y, i = predModel

# ar = np.array(predModel[1].indices)
# distArray = np.array(predModel[1].values)
# print(ar)
print(predModel)
# distInd = 0
# for a in ar:
#   EdgeList.append(Edge(a[0],a[1],float(distArray[distInd])))

#   distInd = distInd + 1
# print(EdgeList[0].node1)





  

# ar = ar[ar == 0 ]
# print(ar)
# # print("Done. Test loss: {:.4f}. Test acc: {:.2f}".format(test_loss, test_acc))

predictedAttribute = np.array(predModel)
reg = 0
for i in range(10):
  for j in range(10):
    for k in range(10):
      resizeImageArray[i][j][k] = predictedAttribute[reg]
      reg = reg + 1

print(resizeImageArray)

print(predModel)

print(len(dataset))

tempSuperPixel = np.zeros((100,230,300),int)

for i in range(100):
  for j in range(230):
    for k in range(300):
        tempSuperPixel[i][j][k] = 1000
      # print(predictedArray[tempSuperPixel[i][j][k]])

def executeErosion(img):
  # eroded = morphology.erosion(img,np.ones([2,2]))
   dilation = morphology.dilation(img,np.ones([2,2]))
  #  dilation2 = morphology.dilation(dilation,np.ones([4,4]))
  #  eroded2 = morphology.erosion(dilation,np.ones([4,4]))
  #  dilation2 = morphology.dilation(eroded2,np.ones([5,5]))
  #  dilation3 = morphology.dilation(dilation2,np.ones([5,5]))
  #  dilation4 = morphology.dilation(dilation3,np.ones([5,5]))
   #erosion2 = morphology.erosion(dilation,morphology.diamond(3))
   return dilation

dilatedImage = []
for i in cropImageArray[20:320]:
  dilatedImage.append(executeErosion(i))

for i in cropImageArray[300:320]:
  plt.imshow(i)
  plt.show()

for i in range(150):
  print(cropImageArray[300][i])

verts, faces, norm, val = measure.marching_cubes_lewiner(np.array(cropImageArray[20:320]),300, step_size=2, allow_degenerate=True) 
x,y,z = zip(*verts)
print(len(x))

pip install trimesh

import trimesh
# mesh = trimesh.load_mesh('mesh.stl')
mesh = trimesh.Trimesh(vertices=verts,
                       faces=faces
                       )
mesh.show()



colormap=['rgb(236, 236, 212)','rgb(236, 236, 212)']

fig = FF.create_trisurf(x=x,
                       y=y, 
                       z=z, 
                       plot_edges=False,
                       colormap=colormap,
                       simplices=faces,
                       edges_color = 'rgb(0, 0, 0)', 
                       backgroundcolor='rgb(64, 64, 64)',
                       title="Interactive Visualization")
iplot(fig)

# for a in A_Test:
dist = np.array(A_Test.data)
EdgeList = []
ind = 0
for i in range(1000):
  for j in range(1000):
    if i != j :
      EdgeList.append(Edge(i,j,dist[ind]))
      ind = ind + 1

faces = []
it = 0 
# dim = 21 * 50
# b = np.zeros((dim,3))
# print(np.array(b))
for n in range(1000):
  adjList = []
  for x in EdgeList:
    if x.node1 == n:
      adjList.append(x)
  # sortList = sorted(adjList, key=lambda adjObj: float(adjObj.weight), reverse=True)
  adjList.sort(key=lambda x: x.weight)
  combArray = []
  for p in range(5):
    if p < len(adjList):
      combArray.append(adjList[p].node2)
      print(str(adjList[p].node1) + ' ' + str(adjList[p].node2) + ' ' + str(adjList[p].weight))

  comb = combinations(combArray, 2)


  
  for x in comb:
    faces.append([])
    npComb = np.array(x)
    faces[it].append(n)
    faces[it].append(npComb[0])
    faces[it].append(npComb[1])
    # b[it][0] = int(n)
    # b[it][1] = int(npComb[0])
    # b[it][2] = int(npComb[1])
    it = it+1
# print(np.array(b))
# faces.append(b)

# print(np.array(faces))
# vertices = np.array(vertices)
# faces = np.array(faces)
# print(faces)

# print(list(np.array(b)))

# faces = b
# faces = list(faces)
# print(faces.shape[0])
# print(list(b))
# print(faces[22][0])

X_cord = []
Y_cord = []
Z_cord = []
f = open("graph.ply", "a")


#open and read the file after the appending:


for c in sp_coord:
  print(c[1])
  # f.write(str(c[0]) + " " + str(c[1]) + " " + str(c[2]))
  # f.write("\n")
f.close()
# f = open("demofile2.txt", "r")
# print(f.read())

# fig = go.Figure(data=[go.Mesh3d(x=X_cord, y=Y_cord, z=Z_cord, color='lightpink', opacity=0.50)])
# fig.show()

pip install numpy-stl

from stl import mesh
shape = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
for i, f in enumerate(faces):
    for j in range(3):
        shape.vectors[i][j] = vertices[f[j], :]

shape.save("Femur4.stl")

pip install trimesh

import trimesh
mesh = trimesh.load_mesh('mesh.stl')
mesh.show()

pip install trimesh

import numpy as np
import trimesh

f = open("demofile2.txt", "a")
f.write("Now the file has more content!")
f.close()

#open and read the file after the appending:
f = open("demofile2.txt", "r")
print(f.read())

class Face:
  def __init__(self, edge, edgeWeight, neighbour, currentNode):
    self.edge = edge
    self.edgeWeight = edgeWeight
    self.neighbour = neighbour
    self.currentNode = currentNode 
  def makeFace(self)
    for 



p1 = Person("John", 36)

print(p1.name)
print(p1.age)

import numpy as np

arr = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])
dist = np.array([1,0])
bollArray = arr[0:len(arr), 1]
c = bollArray == 7
dist = (dist)[c]
print(c)
print(dist)

class Employee:
 
    def __init__(self, name, dept, age):
        self.name = name
        self.dept = dept
        self.age = age
 
    def __repr__(self):
        return '{' + self.name + ', ' + self.dept + ', ' + str(self.age) + '}'
 
 
if __name__ == '__main__':
 
    employees = [
        Employee('John', 'IT', 0),
        Employee('Sam', 'Banking', 0.000000045),
        Employee('Joe', 'Finance', 0.001)
    ]
 
    sortedByName = sorted(employees, key=lambda x: x.age)
 
    # output: [{Joe, Finance, 25}, {John, IT, 28}, {Sam, Banking, 20}]
    print(sortedByName)