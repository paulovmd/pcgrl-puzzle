# -*- coding: utf-8 -*-
import os

RESOURCES_PATH = os.path.dirname(__file__) + "/resources/"

from pcgrl.envs.maze import *
from pcgrl.envs.maze.MazeLevelObjects import *
from pcgrl.envs.maze.MazeGameProblem import MazeGameProblem