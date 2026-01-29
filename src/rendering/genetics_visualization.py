"""
Genetics Visualization module for the simulation.
This module handles the genetics menu (G) display functionality.
"""

import pygame
import math
from collections import defaultdict
from .menu_G.genetics_main import GeneticsVisualization as GeneticsVisualizationRefactored


# Re-export the main class to maintain backward compatibility
GeneticsVisualization = GeneticsVisualizationRefactored