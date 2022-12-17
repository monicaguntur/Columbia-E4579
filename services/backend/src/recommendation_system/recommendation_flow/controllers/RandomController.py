from src.recommendation_system.recommendation_flow.candidate_generators.UserPreferenceGenerator import (
    UserPreferenceGenerator
)

from src.recommendation_system.recommendation_flow.candidate_generators.CFGenerator import (
    CFGenerator
)

from src.recommendation_system.recommendation_flow.candidate_generators.RandomGenerator import (
    RandomGenerator
)

from src.recommendation_system.recommendation_flow.controllers.AbstractController import (
    AbstractController,
)

from src.recommendation_system.recommendation_flow.filtering.RandomFilter import (
    RandomFilter,
)

from src.recommendation_system.recommendation_flow.model_prediction.RandomModel import (
    RandomModel
)

from src.recommendation_system.recommendation_flow.model_prediction.RuleBasedModel import (
    RuleBasedModel,
)

from src.recommendation_system.recommendation_flow.ranking.RandomRanker import (
    RandomRanker,
)

class RandomController(AbstractController):
    def get_content_ids(self, user_id, limit, offset, seed, starting_point):
        candidates_limit = (
            limit * 10 * 10
        )

        if user_id == 0:
            candidates, scores = RandomGenerator().get_content_ids(
                user_id, candidates_limit, offset, seed, starting_point
            )
        else:
            candidates_1, scores_1 = UserPreferenceGenerator().get_content_ids(
                user_id, candidates_limit, offset, seed, starting_point
            )

            candidates_2, scores_2 = CFGenerator().get_content_ids(
                user_id, candidates_limit, offset, seed, starting_point
            )

            print(f"num candidates: {len(candidates_1)}")
            print(f"num candidates: {len(candidates_2)}")

            candidates = candidates_1 + candidates_2
            scores = None



        filtered_candidates = RandomFilter().filter_ids(
            candidates, seed, starting_point
        )

        if user_id == 0:
            predictor_model = RandomModel()
        else:
            predictor_model = RuleBasedModel()

        predictions = predictor_model.predict_probabilities(
            filtered_candidates,
            user_id,
            seed=seed,
            scores={
                content_id: {"score": score}
                for content_id, score in zip(candidates, scores)
            }
            if scores is not None
            else {},
        )

        rank = RandomRanker().rank_ids(limit, predictions, seed, starting_point)

        return rank
