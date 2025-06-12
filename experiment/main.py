
import sys
import os

# Adiciona a pasta raiz do projeto ao caminho de módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from training import train_agents
from inference import infer_agents
from utils import get_rewards_threshold
from logging_config import setup_logger
import config as cfg

if __name__ == '__main__':
    # Configuração inicial
    logger = setup_logger()
    
    # Parâmetros do experimento
    board = (2, 3)  # Exemplo de board
    rewards_threshold = get_rewards_threshold(board, cfg.factor_reward)

    # Chamar o treinamento
    if cfg.is_training:
        train_agents(
            agents=cfg.agents, 
            envs=cfg.envs, 
            rewards_threshold=rewards_threshold,
            board=board, 
            m_changes=cfg.max_changes[0]  # Exemplo de uso do max_changes
        )

    # Chamar a inferência
    if cfg.is_inference:
        infer_agents(
            agents=cfg.agents, 
            envs=cfg.envs, 
            rewards_threshold=rewards_threshold,
            board=board, 
            m_changes=cfg.max_changes[0]
        )