# -*- coding: utf-8 -*-
import os

RESOURCES_PATH = os.path.dirname(__file__) + "/resources/"

from pcgrl.envs.mazecoin import *
from pcgrl.envs.mazecoin.MazeCoinLevelObjects import *
from pcgrl.envs.mazecoin.MazeCoinGameProblem import MazeCoinGameProblem