import pandas as pd
import numpy as np

class PopularCategoriesGenerator():

    def get_content_ids(self):

        popular_categories_content = "popular_categories_table/popular_categories_content.csv"
        popular_categories_content_df = pd.read_csv(popular_categories_content)

        ids = popular_categories_content_df.content_id.tolist()

        return ids, None

    def generate_popular_categories_content(self):

        # read engagement data
        engagement = "engagement.csv"
        engagement_df = pd.read_csv(engagement)

        # sum total likes per pic
        like_engagement_df = engagement_df[engagement_df['engagement_type'] == 'Like']
        like_engagement_df['sum_likes'] = like_engagement_df.groupby('content_id')['engagement_value'].transform('sum')

        # content that has been liked + sum likes
        content_likes = like_engagement_df[['content_id', 'sum_likes']].copy()

        # read generated_content_metadata data
        gen_content_metadata = "generated_content_metadata.csv"
        gen_content_metadata_df = pd.read_csv(gen_content_metadata)

        # join content that has been liked and generated_content_metadata
        merged = gen_content_metadata_df.merge(content_likes, how='inner', on='content_id')
        merged_category_sumlikes = merged[['content_id', 'artist_style', 'source', 'sum_likes']].copy()

        # count number of pics in each category
        merged_category_sumlikes['num_pics'] = merged_category_sumlikes.groupby(['artist_style', 'source'])[
            'content_id'].transform('count')

        # sum total likes per category
        merged_category_sumlikes['sum_likes_by_category'] = \
        merged_category_sumlikes.groupby(['artist_style', 'source'])['sum_likes'].transform('sum')
        content_category = merged_category_sumlikes[
            ['artist_style', 'source', 'sum_likes_by_category', 'num_pics']].drop_duplicates()

        # identify popular categories -> >= 5 total likes
        popular_categories = content_category[content_category['sum_likes_by_category'] >= 5].sort_values(
            ['sum_likes_by_category'], ascending=False).reset_index().drop(columns=['index'])

        # get all pictures in the popular categories
        content_in_popular_categories = gen_content_metadata_df.merge(popular_categories, how='inner',
                                                                      on=['artist_style', 'source'])
        content_ids = content_in_popular_categories[['content_id']]
        content_ids.to_csv('popular_categories_content.csv', index=False)
