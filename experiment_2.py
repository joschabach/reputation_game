# -*- coding: utf-8 -*-

"""
Definition of agents and simulation function
"""

__author__ = 'joscha'
__date__ = '08.07.14'



from experiment_1 import *


Settings.number_of_agents = 100
Settings.number_of_simulation_steps_in_a_generation = 300
Settings.number_of_generations = 2000
Settings.influence_of_fitness_to_reproductive_success = 0.99
Settings.number_of_parents_in_a_generation = 50
Settings.mutation_rate = 0.01




class StrategyPlot(Diagram):
    key = "strategy"
    window_title = "Average strategy"

    def plot(self):
        data = self.simulation.log[:self.simulation.current_generation]["strategy"]
        if len(data):
            self.subplot.cla()
            self.subplot.plot(data.mean(axis=1), color="brown", linewidth=1.0)


diagrams = [ ValuePlot, StrategyPlot, StrategyHistogram ]


