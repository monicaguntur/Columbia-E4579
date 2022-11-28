import operator

from src import db
from src.data_structures.approximate_nearest_neighbor import ann_with_offset

from .AbstractGenerator import AbstractGenerator
from .RandomGenerator import RandomGenerator


class EngagementTimeGenerator(AbstractGenerator):
    def get_content_ids(self, user_id, limit, offset, seed, starting_point):

        if starting_point is None:
            # get the preference from the user
            with db.engine.connect() as con:
                query = """select
                                engagement.content_id as content_id,
                                sum(engagement.engagement_value) as engagement_time
                            from
                                (
                                    select
                                        distinct engagement.content_id as content_id
                                    from
                                        engagement
                                    where
                                        engagement.user_id = """ + str(user_id) + """
                                        and (
                                            engagement.engagement_type = "like"
                                            and engagement.engagement_value = 1
                                        )
                                ) temp
                                left join engagement on engagement.content_id = temp.content_id
                            where
                                engagement.user_id = """ + str(user_id) + """ 
                            group by
                                engagement.content_id
                            having 
                                engagement_time < 600000
                            order by
                                engagement_time desc
                            limit """ + str(limit) + """;
                            """

            results = con.execute(query).all()

            num_results = len(results)

            # if no previous record then do random cg
            if num_results == 0:
                return RandomGenerator().get_content_ids(
                    user_id, limit, offset, seed, starting_point
                )
                
            # get 2x so we can take the best
            new_limit = 2 * (limit // num_results + 1)
            new_offset = offset // num_results + 1
            new_result, new_scores = [], []
            for (content_id, ms) in results:
                # can probably do this faster as a heap so instead of `2 * limit * (1+log2(limit))` in `limit * log2(limit)`
                content_ids, scores = ann_with_offset(
                    content_id, 0.9, 2 * new_limit, new_offset, return_distances=True
                )
                new_result.extend(content_ids)
                # TODO: score and ms should probably be normalized so multiplication makes sense
                new_scores.extend(map(lambda score: score * ms, scores))
            if len(new_result) == 0:
                return RandomGenerator().get_content_ids(
                    user_id, limit, offset, seed, starting_point
                )
            results_with_scores = sorted(
                list(zip(new_result, new_scores)), key=operator.itemgetter(1)
            )[:limit]
            return list(map(operator.itemgetter(0), results_with_scores)), list(
                map(operator.itemgetter(1), results_with_scores)
            )
        elif starting_point.get("content_id", False):
            content_ids, scores = ann_with_offset(
                starting_point["content_id"], 0.9, limit, offset, return_distances=True
            )
            return content_ids, scores
        raise NotImplementedError("Need to provide a key we know about")
