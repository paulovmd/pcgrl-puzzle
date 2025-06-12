from pcgrl.utils.experiment import Experiment
from config import *

def get_rewards_threshold(board, factor_reward):
    """
    Função para obter os thresholds de recompensa com base no board.
    """
    if board == (2, 3):
        return {
            Experiment.AGENT_SS.value: 2.3 * factor_reward,
            Experiment.AGENT_HHP.value: 2.3 * factor_reward,
            Experiment.AGENT_HEQHP.value: 7.9 * factor_reward
        }
    elif board == (2, 4):
        return {
            Experiment.AGENT_SS.value: 2.8 * factor_reward,
            Experiment.AGENT_HHP.value: 2.8 * factor_reward,
            Experiment.AGENT_HEQHP.value: 8.3 * factor_reward
        }
    return {}
