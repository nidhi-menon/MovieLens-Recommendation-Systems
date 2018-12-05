
# coding: utf-8
'''
File name: IBCF.py
Implementation: Item-Based Collaborative Filtering
Author: Nidhi N. Menon
Date created: 11/14/2018
Date last modified: 3/12/2018
Python Version: 2.7
'''

# In[1]:


import pandas as pd
import pickle
import os.path


# In[2]:


r_cols = ['user_id', 'movie_id', 'rating']
ratings = pd.read_csv('../data/ml-100k-DATA/u.data', sep='\t', names=r_cols, usecols=range(3))

m_cols = ['movie_id', 'title']
movies = pd.read_csv('../data/ml-100k-DATA/u.item', sep='|', names=m_cols, usecols=range(2))

ratings = pd.merge(movies, ratings)
ratings.head(10)


# In[3]:


userRatings_data = ratings.pivot_table(index=['user_id'],columns=['title'],values='rating')
userRatings_data.head()


# In[4]:


# save the model to disk
filename1 = 'IBCF_UR.sav'
path1 = '../models/'
completeName1 = os.path.join(path1, filename1)
pickle.dump(userRatings_data, open(completeName1, 'wb'))


# In[5]:


corrMatrix_data = userRatings_data.corr()
corrMatrix_data.head()


# In[6]:


corrMatrix_data = userRatings_data.corr(method='pearson', min_periods=100)
corrMatrix_data.head()


# In[7]:


# save the model to disk
filename1 = 'IBCF_CM.sav'
path1 = '../models/'
completeName1 = os.path.join(path1, filename1)
pickle.dump(corrMatrix_data, open(completeName1, 'wb'))


# In[8]:


'''
import time

start_time = time.time()
print 'Start Time: '
print start_time
'''


# In[9]:


# load the model from disk
userRatings = pickle.load(open('../models/IBCF_UR.sav', 'rb'))


# In[10]:


# load the model from disk
corrMatrix = pickle.load(open('../models/IBCF_CM.sav', 'rb'))


# In[11]:


print "Movies and their ratings for custom user 944"
#Can change to any user ID to obtain recommendation for that user
myRatings = userRatings.loc[944].dropna()
myRatings


# In[12]:


similarCandidates = pd.Series()
for i in range(0, len(myRatings.index)):
    print "adding similarities for " + myRatings.index[i] + "..."
    similarities = corrMatrix[myRatings.index[i]].dropna()
    similarities = similarities.map(lambda x: x * myRatings[i])
    similarCandidates = similarCandidates.append(similarities)
    
print "sorting in decreasing order of similarity score: "
similarCandidates.sort_values(inplace = True, ascending = False)
print similarCandidates.head(10)


# In[13]:


similarCandidates = similarCandidates.groupby(similarCandidates.index).sum()


# In[14]:


'''
print "Adding up the similarity scores of duplicate values:"
similarCandidates.sort_values(inplace = True, ascending = False)
similarCandidates.head(10)
'''


# In[15]:


print "Filtering the result to remove already rated movies:"
filteredSimilarities = similarCandidates.drop(myRatings.index, errors='ignore')
filteredSimilarities.sort_values(inplace = True, ascending = False)
filteredSimilarities.head(25)


# In[16]:


'''
end_time = time.time()
print 'End Time: '
print end_time
'''


# In[17]:


'''
total_time = time.time() - start_time
print 'Total Time: '
print total_time
'''

