from pcgrl.utils.experiment import ExperimentManager
from config import *

def run_inference(experiment_manager, time_steps_inference, render, record_video, show_hud):
    """
    Função para rodar a inferência de um experimento.
    """
    experiment_manager.inference(
        time_steps=time_steps_inference,
        use_function_set_random_seed=True,
        render=render,
        record_video=record_video,
        show_hud=show_hud
    )

def infer_agents(agents, envs, rewards_threshold, board, m_changes):
    """
    Função para iniciar a inferência de todos os agentes.
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
                policy_kwargs=policy_kwargs
            )
            run_inference(experiment_manager, time_steps_inference, render, record_video, show_hud)
