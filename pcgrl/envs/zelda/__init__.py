# -*- coding: utf-8 -*-
import os

RESOURCES_PATH = os.path.dirname(__file__) + "/resources/"

from pcgrl.envs.zelda import *
from pcgrl.envs.zelda.ZeldaLevelObjects import *
from pcgrl.envs.zelda.ZeldaGameProblem import ZeldaGameProblem
