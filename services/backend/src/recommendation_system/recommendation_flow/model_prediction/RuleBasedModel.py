from src import db

from .AbstractModel import AbstractModel

class RuleBasedModel(AbstractModel):
    def liked_same_style(self, con, content_id, user_id):
        # If the user has liked images from this category +1 to the score, else 0

        # first get the style
        style_query = 'SELECT artist_style '\
                'FROM generated_content_metadata '\
                f'WHERE id={content_id};'
        style = con.execute(style_query).one()[0]

        liked_same_style_query = 'SELECT COUNT(engagement.content_id) '\
                                'FROM engagement LEFT JOIN generated_content_metadata '\
                                'ON engagement.content_id=generated_content_metadata.content_id '\
                                f'WHERE engagement.user_id={user_id} AND '\
                                'engagement.engagement_type="Like" AND '\
                                'engagement.engagement_value=1 AND '\
                                f'generated_content_metadata.artist_style="{style}";'
        result = con.execute(liked_same_style_query).one()[0]

        return result > 0
    
    def popularity_score(self, con, content_id):
        # If ratio of likes/(likes+dislikes) > threshold  +1 to the score, else 0
        likes_query = 'SELECT COUNT(*) '\
                'FROM engagement '\
                f'WHERE content_id={content_id} AND '\
                'engagement_type="Like" AND '\
                'engagement_value=1;'

        dislikes_query = 'SELECT COUNT(*) '\
                'FROM engagement '\
                f'WHERE content_id={content_id} AND '\
                'engagement_type="Like" AND '\
                'engagement_value=-1;'

        num_of_likes = con.execute(likes_query).one()[0]
        num_of_dislikes = con.execute(dislikes_query).one()[0]
        total_score = num_of_likes+num_of_dislikes
        return num_of_likes*1.0/total_score > 0.5 if total_score > 0 else False

    def calculate_score(self, content_id, user_id):
        score = 0
        with db.engine.connect() as con:
            score += int(self.liked_same_style(con, user_id, content_id))
            score += int(self.popularity_score(con, content_id))
        
        return score

    def predict_probabilities(self, content_ids, user_id, seed=None, **kwargs):
        return list(
            map(
                lambda content_id: {
                    "content_id": content_id,
                    "p_engage": self.calculate_score(content_id, user_id),
                    "score": kwargs.get("scores", {})
                    .get(content_id, {})
                    .get("score", None),
                },
                content_ids,
            )
        )
