# experiment/__init__.py

# Opcional: torna mais fácil importar funções específicas
from .training import train_agents
from .inference import infer_agents
from .utils import get_rewards_threshold
from .config import *

# Lista de itens expostos se alguém usar "from experiment import *"
__all__ = [
    "train_agents",
    "infer_agents",
    "get_rewards_threshold"
]