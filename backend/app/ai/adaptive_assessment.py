import numpy as np
from typing import List, Dict, Any

class AdaptiveAssessmentIRT:
    """
    Implements Item Response Theory (IRT) for adaptive mental health assessments.
    Reduces user burden by choosing questions that provide the most information 
    based on previous answers.
    
    Model: 2-Parameter Logistic (2PL)
    P(x=1|theta) = 1 / (1 + exp(-a * (theta - b)))
    where theta = estimated latent trait (e.g., depression level)
          a = item discrimination (how well question distinguishes between levels)
          b = item difficulty (threshold for positive response)
    """
    
    # PHQ-9 Item Parameters (Mocked based on common psychometric data)
    PHQ9_PARAMS = {
        1: {"a": 1.2, "b": 0.5, "text": "Little interest or pleasure in doing things?"},
        2: {"a": 1.5, "b": 0.8, "text": "Feeling down, depressed, or hopeless?"},
        3: {"a": 0.8, "b": 1.2, "text": "Trouble falling or staying asleep, or sleeping too much?"},
        4: {"a": 1.1, "b": 0.3, "text": "Feeling tired or having little energy?"},
        5: {"a": 0.9, "b": 1.5, "text": "Poor appetite or overeating?"},
        6: {"a": 1.3, "b": 1.0, "text": "Feeling bad about yourself or that you are a failure?"},
        7: {"a": 0.7, "b": 1.8, "text": "Trouble concentrating on things, such as reading?"},
        8: {"a": 1.0, "b": 0.4, "text": "Moving or speaking so slowly that other people could have noticed?"},
        9: {"a": 2.0, "b": 2.5, "text": "Thoughts that you would be better off dead or of hurting yourself?"},
    }

    @staticmethod
    def get_next_item(responses: Dict[int, int], theta_est: float = 0.0) -> Optional[int]:
        """
        Selects the next question that provides the maximum Fisher Information 
        at the current estimated theta level.
        """
        remaining_ids = [i for i in range(1, 10) if i not in responses]
        if not remaining_ids:
            return None
            
        best_item = None
        max_info = -1.0
        
        for item_id in remaining_ids:
            param = AdaptiveAssessmentIRT.PHQ9_PARAMS[item_id]
            a, b = param["a"], param["b"]
            
            # Probability of positive response (score >= 2)
            p = 1.0 / (1.0 + np.exp(-a * (theta_est - b)))
            # Information function I(theta) = a^2 * p * (1 - p)
            info = (a**2) * p * (1.0 - p)
            
            if info > max_info:
                max_info = info
                best_item = item_id
                
        return best_item

    @staticmethod
    def estimate_theta(responses: Dict[int, int]) -> float:
        """
        Estimates the latent trait (theta) using Maximum Likelihood Estimation (MLE).
        For simplicity in this MVP, we use a weighted average of difficulties.
        In production, we would use Newton-Raphson to solve for theta.
        """
        if not responses:
            return 0.0
            
        weights = []
        difficulties = []
        
        for item_id, score in responses.items():
            # Normalized score (0-3) -> (0.0 to 1.0)
            weight = score / 3.0
            param = AdaptiveAssessmentIRT.PHQ9_PARAMS[item_id]
            
            weights.append(weight)
            difficulties.append(param["b"])
            
        # Weighted average of difficulty parameters
        return np.average(difficulties, weights=weights) if sum(weights) > 0 else np.mean(difficulties)

    @staticmethod
    def map_theta_to_score(theta: float) -> int:
        """
        Maps the latent theta back to a standard PHQ-9 scale (0-27).
        Approximate mapping: theta range [-3, 3] -> score [0, 27]
        """
        normalized = (theta + 3.0) / 6.0
        return int(max(0, min(27, normalized * 27)))
