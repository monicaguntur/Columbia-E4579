
import heapq
import random

from .AbstractRanker import AbstractRanker


class RandomRanker(AbstractRanker):
    def rank_ids(self, limit, predictions, seed, starting_point):
        k = limit #number to show
        top_k = heapq.nlargest(k, predictions, key=lambda x: x["p_engage"]) # sort by p_engage
        top_k_ids = list(map(lambda x: x["content_id"], top_k))
        if seed:
            random.seed(seed)
        return random.sample(top_k_ids, len(top_k_ids))  # shuffle






