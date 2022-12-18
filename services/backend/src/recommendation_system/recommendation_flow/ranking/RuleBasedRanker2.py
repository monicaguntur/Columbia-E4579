#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import heapq
import random

from .AbstractRanker import AbstractRanker


class RuleBasedRanker(AbstractRanker):
    def rank_ids(self, limit, predictions, seed, starting_point):
        k = limit #total number to show
        
        #80% from score=2, 10% from score=1, 10% from score =0
        score2k=0.8*k
        score1k=0.1*k
        score0k=0.1*k
        
        prediction2=[]
        prediction1=[]
        prediction0=[]
        
        #split to 3 group by score
        for d in prediction:
            if d.get("score")==2:
                prediction2.append(d)
            else if d.get("score")==1:
                prediction1.append(d)
            else if d.get("score")==0:
                prediction0.append(d)
        
        #select best of each 3 group
        top_score2k = heapq.nlargest(score2k, predictions2, key=lambda x: x["p_engage"]) # sort by p_engage
        top_score1k = heapq.nlargest(score1k, predictions1, key=lambda x: x["p_engage"])
        top_score0k = heapq.nlargest(score0k, predictions0, key=lambda x: x["p_engage"])
        
        top_score2k_ids = list(map(lambda x: x["content_id"], top_score2k))
        top_score1k_ids = list(map(lambda x: x["content_id"], top_score1k))
        top_score0k_ids = list(map(lambda x: x["content_id"], top_score0k))
        
        #add selected img together 
        top_k_ids=top_score2k_ids+top_score1k_ids+top_score0k_ids
        
        if seed:
            random.seed(seed)
        
        return random.sample(top_k_ids, len(top_k_ids))  # shuffle


# In[1]:




