# -*- coding: utf-8 -*-

"""
Definition of agents and simulation function
"""

__author__ = 'joscha'
__date__ = '08.07.14'


import experiment_1
from experiment_1 import *


Settings.number_of_agents = 100
Settings.number_of_simulation_steps_in_a_generation = 300
Settings.number_of_generations = 2000
Settings.influence_of_fitness_to_reproductive_success = 0.99
Settings.number_of_parents_in_a_generation = 50
Settings.mutation_rate = 0.1

Settings.noise = 0.5

# todo: 2d-strategy, and stochastic choice

def cooperation_policy(agent, other_agent):
    """Return true to cooperate, false to defect"""
    return agent["strategy"] + (random() - 0.5) * agent["noise"] <= other_agent["reputation"]


class Simulation(experiment_1.Simulation):
    def init_agents(self):
        self.agents = np.zeros(Settings.number_of_agents,
                               dtype=[("value", float), ("reputation", int), ("strategy", int), ("noise", float)])
        self.agents["strategy"] = np.random.randint(-5, 6, size=len(self.agents))
        self.agents["noise"] = Settings.noise


    def mutate_agents(self, agents):
        """called for the array of children of a new generation"""

        strategy = agents["strategy"]
        number_of_mutations = np.random.binomial(Settings.number_of_agents, Settings.mutation_rate)
        strategy[np.random.randint(0, len(strategy),
                                   size=number_of_mutations)] = np.random.randint(-4, 6, size=number_of_mutations)

        noise = agents["noise"]
        number_of_mutations = np.random.binomial(Settings.number_of_agents, Settings.mutation_rate)
        noise[np.random.randint(0, len(noise),
                                size=number_of_mutations)] += (np.random.random(size=number_of_mutations) - 0.5)
        np.clip(noise, 0., 5., out=noise)



    def reset_agents(self, agents):
        """reset agent parameters at the start of a new generation"""
        agents["value"] = 0
        agents["reputation"] = 0

    def _update_log(self, generation = False):
        """adds the current values and reputations to the log"""
        if generation:
            for key in self.log:
                self.log[key].append([agent[key] for agent in self.agents])

class NoisePlot(Diagram):
    key = "noise"
    window_title = "Average level of noise"

    def plot(self):
        data = self.simulation.log[:self.simulation.current_generation]["noise"]
        if len(data):
            self.subplot.cla()
            self.subplot.plot(data.mean(axis=1), color="grey", linewidth=1.0)

from experiment_2 import StrategyPlot

diagrams = [ ValuePlot, StrategyPlot, StrategyHistogram, NoisePlot ]


