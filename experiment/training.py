from utils import get_rewards_threshold
from pcgrl.utils.experiment import ExperimentManager
from config import *

def run_training( experiment_manager : ExperimentManager, render, save_level, show_hud):
    """
    Função para rodar o treinamento de um experimento.
    """
    experiment_manager.learn(
        use_function_set_random_seed=True,
        render=render,
        save_image_level=save_level,
        show_hud=show_hud
    )

def train_agents(agents, envs, rewards_threshold, board, m_changes):
    """
    Função para iniciar o treinamento de todos os agentes.
    """
    for a in agents:
        for e in envs:
            experiment_manager = ExperimentManager(
                policy=policy,
                learning_rate=learning_rate,
                results_dir=path_results,
                n_steps=n_steps,
                agent=[a],
                envs=[e],
                rewards_threshold=rewards_threshold,
                board=board,
                total_timesteps=total_timesteps,
                max_changes=m_changes,
                factor_reward=factor_reward,
                n_epochs=n_epochs,
                batch_size=batch_size,
                policy_kwargs=policy_kwargs
            )
            run_training(experiment_manager, render, save_level, show_hud)
