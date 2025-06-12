import torch as th
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch.nn as nn


# Exemplo de extrator de características customizado para CnnPolicy
class CustomCNNV2(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim=512):
        super().__init__(observation_space, features_dim)
        self.cnn = nn.Sequential(
            nn.Conv2d(observation_space.shape[0], 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten()
        )

        # Calcular tamanho da saída da CNN
        with th.no_grad():
            n_flatten = self.cnn(th.as_tensor(observation_space.sample()[None]).float()).shape[1]

        self.linear = nn.Sequential(
            nn.Linear(n_flatten, features_dim),
            nn.ReLU()
        )

    def forward(self, observations: th.Tensor) -> th.Tensor:
        return self.linear(self.cnn(observations))


# Dicionário de políticas disponíveis para facilitar reuso
POLICIES = {
    "mlp_sigmoid": {
        "policy": "MlpPolicy",
        "kwargs": dict(
            net_arch=[dict(pi=[64, 64], vf=[64, 64])],
            activation_fn=th.nn.Sigmoid
        )
    },
    "mlp_relu": {
        "policy": "MlpPolicy",
        "kwargs": dict(
            net_arch=[dict(pi=[64, 64], vf=[64, 64])],
            activation_fn=th.nn.ReLU
        )
    },
    "mlp_tanh": {
        "policy": "MlpPolicy",
        "kwargs": dict(
            net_arch=[dict(pi=[64, 64], vf=[64, 64])],
            activation_fn=th.nn.Tanh
        )
    },  
    "mlp_softmax": {
        "policy": "MlpPolicy",
        "kwargs": dict(
            net_arch=[dict(pi=[64, 64], vf=[64, 64])],
            activation_fn=th.nn.Softmax
        )
    },        
    "cnn_custom": {
        "policy": "CnnPolicy",
        "kwargs": dict(
            features_extractor_class=CustomCNNV2,
            features_extractor_kwargs={"features_dim": 512}
        )
    }
}


def get_policy(name: str):
    """
    Retorna o tipo de policy e os argumentos para uso no SB3.
    """
    if name not in POLICIES:
        raise ValueError(f"Política '{name}' não encontrada. Opções: {list(POLICIES.keys())}")
    return POLICIES[name]["policy"], POLICIES[name]["kwargs"]
