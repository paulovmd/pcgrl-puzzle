# agents/ppo_agent.py

import torch
import gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

class PPOAgent:
    def __init__(self, env: gym.Env, model_path=None):
        """
        Initialize the PPO agent.
        
        :param env: The gym environment to train the agent on.
        :param model_path: Optional path to a pre-trained model.
        """
        self.env = DummyVecEnv([lambda: env])  # Wrap the environment
        self.model = PPO("MlpPolicy", self.env, verbose=1)
        
        # If a model path is provided, load the model
        if model_path:
            self.model.load(model_path)
        
    def train(self, total_timesteps: int):
        """
        Train the PPO agent.
        
        :param total_timesteps: Total number of timesteps to train the agent.
        """
        self.model.learn(total_timesteps=total_timesteps)
        
    def save(self, model_path: str):
        """
        Save the trained model.
        
        :param model_path: Path to save the model.
        """
        self.model.save(model_path)
        
    def evaluate(self, num_episodes: int):
        """
        Evaluate the agent's performance.
        
        :param num_episodes: Number of episodes to evaluate the agent.
        """
        total_rewards = 0
        for _ in range(num_episodes):
            obs = self.env.reset()
            done = False
            episode_reward = 0
            while not done:
                action, _ = self.model.predict(obs)
                obs, reward, done, info = self.env.step(action)
                episode_reward += reward
            total_rewards += episode_reward
        print(f"Average reward over {num_episodes} episodes: {total_rewards / num_episodes}")
