# Machine Learning-Based Approaches - 2


## Dataset used: `movielens-100k`

## Installation

- As Run on macOS Mojave `Version 10.14.1`
- Download  and Install Anaconda2 v4.5.11 `https://www.anaconda.com/download/#macos`
- Create Conda Environment `conda create -n gl-env python=2.7 anaconda=4.0.0`
- Activate virtual environment `conda activate gl-env`
- Deactivate virtual environment `source deactivate`

- Note: Relative path is used to find dataset folder 'ml-100k', please comment out lines specifying paths `"/Users/snehavenkat/Desktop/BDS/ml-100k"` in case the code is tested, and replace with the relative path for the folder on your system

## Collaborative Filtering Approach using KMeans clustering

- File name: `kMeans.ipynb`
- To run the file,
a) Activate virtual environment using command `conda activate gl-env`
b) Run jupyter notebook using command  `jupyter notebook`
c) Open file `kMeans.ipynb`
- Libraries used:
`numpy
pandas
KMeans (from sklearn.cluster)
train_test_split (from sklearn.cross_validation)
preprocessing (from sklearn)
accuracy_score (from sklearn.metrics)
time
pickle
sys
cdist (from scipy.spatial.distance)
silhouette_samples (from sklearn.metrics)
silhouette_score (from sklearn.metrics)
matplotlib.pyplot`

## Content-Based Filtering Approach using TF-IDF

- File name: `Content-based_2.ipynb`
- To run the file,
a) Activate virtual environment using command `conda activate gl-env`
b) Run jupyter notebook using command  `jupyter notebook`
c) Open file `Content-based_2.ipynb`
- Libraries used:
`numpy
NearestNeighbors (from sklearn.neighbors)
Evaluator (from evaluator)
DatasetHandler(from dataset_handler)
pandas
time
pickle
TfidfVectorizer (from sklearn.feature_extraction.text)
linear_kernel (from sklearn.metrics.pairwise)`

## Content-Based Filtering Approach using Cosine KNN

- File name: `Content-based_1.ipynb`
- Dependent files: `evaluator.py, dataset_handler.py`
- Dependent data files (in addition to files in the movielens folder: ml-100k) `movies.csv, ratings.csv`
- To run the file,
a) Activate virtual environment using command `conda activate gl-env`
b) Run jupyter notebook using command  `jupyter notebook`
c) Open file `Content-based_1.ipynb`
- Libraries used:
`pandas
numpy
time
pickle
sys`

## Important Note for Code References:

- Collaborative filtering (KMeans):
`https://github.com/TaihuaLi/Movielens-Recommender`
- Content-Based filtering:
 -TF-IDF approach
 `https://medium.com/@james_aka_yale/the-4-recommendation-engines-that-can-predict-your-movie-tastes-bbec857b8223`
 -Cosine KNN approach
 `https://github.com/smalec/movielens/blob/master/ContentBased.ipynb`
