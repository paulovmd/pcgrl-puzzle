import os
from pcgrl.utils.experiment import Experiment
from pcgrl import Game

# Definindo os parâmetros do experimento
rl_algo = "PPO"
act_func = "SIGMOID"
n_experiment = 1
total_timesteps = 100000
learning_rate = 3e-4
n_steps = 2048  # Horizonte do PPO
gamma = 0.99
batch_size = 64
n_epochs = 10
max_changes = [21, 61, 180]
time_steps_inference = 1000
entropy_min = None
reward_best_done_bonus = 50
reward_medium_done_bonus = 10
reward_low_done_bonus = 0
reward_entropy_penalty = 0
reward_change_penalty = -0.1
boards = [(2, 3), (2, 4)]
path_results = "C:\\Experimentos\\results-threshold"
seeds = [42]
factor_reward = 1
render = False
show_hud = False
show_logger = False
record_video = False
action_change = False
action_rotate = False
env_rewards = False
save_level = False
piece_size = 8
is_training = True
is_inference = True
plot_results_experiments = False

# Definindo a política
policy = "MlpPolicy"
policy_kwargs = {
    "net_arch": [64, 64],
    "activation_fn": "Sigmoid"
}

agents = [Experiment.AGENT_SS.value, Experiment.AGENT_HHP.value, Experiment.AGENT_HEQHP.value]  # Exemplo de agentes
envs = [Game.ZELDALOWMAPS.value]                # Exemplo de ambientes

# Verifica se o diretório existe, se não existir, cria
if not os.path.exists(path_results):
    os.makedirs(path_results)
    print(f"Diretório criado: {path_results}")
else:
    print(f"Diretório já existe: {path_results}")