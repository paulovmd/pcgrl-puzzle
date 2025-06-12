from enum import Enum

class AgentBehaviorType(str, Enum):
    SS = "strict_satisfaction"
    HHP = "hard_high_precision"
    HEQHP = "entropy_quality_high_precision"

def get_behavior_config(behavior: AgentBehaviorType):
    if behavior == AgentBehaviorType.SS:
        return {
            "reward_best_done_bonus": 50,
            "reward_medium_done_bonus": 10,
            "reward_low_done_bonus": 0,
            "reward_entropy_penalty": 0,
            "reward_change_penalty": -0.1,
            "factor_reward" : 1
        }
    elif behavior == AgentBehaviorType.HHP:
        return {
            "reward_best_done_bonus": 70,
            "reward_medium_done_bonus": 5,
            "reward_low_done_bonus": 0,
            "reward_entropy_penalty": 0.05,
            "reward_change_penalty": -0.2,
            "factor_reward" : 1
        }
    elif behavior == AgentBehaviorType.HEQHP:
        return {
            "reward_best_done_bonus": 80,
            "reward_medium_done_bonus": 20,
            "reward_low_done_bonus": 5,
            "reward_entropy_penalty": 0.1,
            "reward_change_penalty": -0.05,
            "factor_reward" : 1
        }
    else:
        raise ValueError(f"Comportamento {behavior} não reconhecido")


            