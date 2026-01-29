"""
Statistics Visualization module for the simulation.
This module handles the statistics menu (S) display functionality.
"""

import pygame
import math
from collections import defaultdict
from .menu_S.stats_visualization import StatsVisualization as StatsVisualizationRefactored


# Re-export the main class to maintain backward compatibility
StatsVisualization = StatsVisualizationRefactored