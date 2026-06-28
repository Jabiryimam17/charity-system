PROPOSAL_LEVELS = ['L1', 'L2', 'L3', 'L4', 'L5']
HIGHEST_LEVEL = PROPOSAL_LEVELS[-1]  # 'L5'

QUESTION_MIN = 1
QUESTION_MAX = 10

LEVEL_PROMOTION_REQUIREMENTS = {
    'L1': {'min_reviewers': 3, 'score_threshold': 0.40},
    'L2': {'min_reviewers': 7, 'score_threshold': 0.55},
    'L3': {'min_reviewers': 12, 'score_threshold': 0.70},
    'L4': {'min_reviewers': 20, 'score_threshold': 0.85},
}

# upper bound of each level as a percentage [0, 100]
LEVEL_THRESHOLDS = [
    (20,  'L1'),
    (40,  'L2'),
    (60,  'L3'),
    (80,  'L4'),
    (100, 'L5'),
]

def get_next_level(current_level: str) -> str | None:
    idx = PROPOSAL_LEVELS.index(current_level)
    if idx + 1 >= len(PROPOSAL_LEVELS):
        return None
    return PROPOSAL_LEVELS[idx + 1]