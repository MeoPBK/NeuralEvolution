"""
Species History Visualization module for the simulation.
This module handles the species history menu (H) display functionality.
"""

import pygame
import math
from collections import defaultdict
from .menu_H.species_history import SpeciesHistoryVisualization as SpeciesHistoryVisualizationRefactored


# Re-export the main class to maintain backward compatibility
SpeciesHistoryVisualization = SpeciesHistoryVisualizationRefactored