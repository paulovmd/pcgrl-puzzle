# -*- coding: utf-8 -*-
import os

RESOURCES_COMBAT_PATH = os.path.dirname(__file__) + "/resources/combat"

from pcgrl.envs.combat import *
from pcgrl.envs.combat.CombatGameProblem import CombatGameProblem
from pcgrl.envs.combat.CombatEnv import CombatEnv