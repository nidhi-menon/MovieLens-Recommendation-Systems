
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


import csv
import pandas as pd
import numpy as np
import pickle
import os.path


# In[2]:


ratings_df = pd.read_csv('../models/ml-100k-CSV/ratings.csv')
ratings_df.head()


# In[3]:


movies_df = pd.read_csv('../models/ml-100k-CSV/movies.csv')
movies_df.head()


# In[4]:


R_df = ratings_df.pivot(index = 'UserID', columns ='MovieID', values = 'Rating').fillna(0)
R_df.head()


# In[5]:


R = R_df.as_matrix()
user_ratings_mean = np.mean(R, axis = 1)
R_demeaned = R - user_ratings_mean.reshape(-1, 1)


# In[6]:


from scipy.sparse.linalg import svds
U, sigma, Vt = svds(R_demeaned, k = 50)


# In[7]:


sigma = np.diag(sigma)


# In[8]:


all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
all_user_predicted_ratings


# In[9]:


preds_df_data = pd.DataFrame(all_user_predicted_ratings, columns = R_df.columns)
preds_df_data.head()


# In[10]:


# save the model to disk
filename1 = 'MF.sav'
path1 = '../models/'
completeName1 = os.path.join(path1, filename1)
pickle.dump(preds_df_data, open(completeName1, 'wb'))


# In[11]:


# load the model from disk
preds_df = pickle.load(open(filename, 'rb'))


# In[12]:


def recommend_movies(predictions_df, userID, movies_df, original_ratings_df, num_recommendations=5):
    
    # Get and sort the user's predictions
    user_row_number = userID - 1 # UserID starts at 1, not 0
    sorted_user_predictions = preds_df.iloc[user_row_number].sort_values(ascending=False) # UserID starts at 1
    
    # Get the user's data and merge in the movie information.
    user_data = original_ratings_df[original_ratings_df.UserID == (userID)]
    user_full = (user_data.merge(movies_df, how = 'left', left_on = 'MovieID', right_on = 'MovieID').
                     sort_values(['Rating'], ascending=False)
                 )

    print 'User {0} has already rated {1} movies.'.format(userID, user_full.shape[0])
    print 'Recommending highest {0} predicted ratings movies not already rated.'.format(num_recommendations)
    
    # Recommend the highest predicted rating movies that the user hasn't seen yet.
    recommendations = (movies_df[~movies_df['MovieID'].isin(user_full['MovieID'])].
         merge(pd.DataFrame(sorted_user_predictions).reset_index(), how = 'left',
               left_on = 'MovieID',
               right_on = 'MovieID').
         rename(columns = {user_row_number: 'Predictions'}).
         sort_values('Predictions', ascending = False).
                       iloc[:num_recommendations, :-1]
                      )

    return user_full, recommendations


# In[13]:


already_rated, predictions = recommend_movies(preds_df, 944, movies_df, ratings_df, 25)


# In[14]:


already_rated.head(10)


# In[15]:


predictions

