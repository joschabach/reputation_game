# -*- coding: utf-8 -*-

"""
Definition of agents and simulation function
"""

__author__ = 'joscha'
__date__ = '20.06.14'

from random import randint, random

from widgets import Settings
from helper_widgets import Diagram
import numpy as np

import simulation_numpy as simulation


Settings.number_of_agents = 100
Settings.number_of_parents_in_a_generation = 100
Settings.number_of_surviving_agents = 0
Settings.number_of_simulation_steps_in_a_generation = 125
Settings.number_of_generations = 150
Settings.influence_of_fitness_to_reproductive_success = 1.0
Settings.mutation_rate = 0.0


def cooperation_policy(agent, other_agent):
    """Return true to cooperate, false to defect"""
    return agent["strategy"] <= other_agent["reputation"]


class Simulation(simulation.Simulation):

    def init_agents(self):
        self.agents = np.zeros(Settings.number_of_agents,
                               dtype=[("value", float), ("reputation", int), ("strategy", int)])
        self.agents["strategy"] = np.random.randint(-5, 6, size=len(self.agents))


    def step(self):
        """Advances the simulation by a single step. Returns False if we are done"""
        if self.current_simstep < Settings.number_of_simulation_steps_in_a_generation:
            self.cooperation_step()
            self.current_simstep += 1
            return True
        else:
            if self.current_generation < Settings.number_of_generations:
                self.log[self.current_generation] = self.agents
                self.select_agents()
                self.current_generation += 1
                self.current_simstep = 0
                return True
        return False




    def mutate_agents(self, agents):
        """called for the array of children of a new generation"""

        agents = agents["strategy"]
        #selector = [np.random.rand(*agents.shape) < Settings.mutation_rate]
        #agents[selector] = np.random.randint(-4, 6, size = len(selector))

        # if the mutation rate is low, it should be faster to select the mutated children directly
        number_of_mutations = np.random.binomial(Settings.number_of_agents, Settings.mutation_rate)
        agents[np.random.randint(0, len(agents),
                                 size=number_of_mutations)] = np.random.randint(-4, 6, size = number_of_mutations)



    def reset_agents(self, agents):
        """reset agent parameters at the start of a new generation"""
        agents["value"] = 0
        agents["reputation"] = 0

    def cooperation_step(self, display_steps = True):
        a, b = self._get_two_agents()

        min_reputation = -5
        max_reputation = 5

        cooperation = cooperation_policy(a, b)
        if cooperation:  # agent cooperates
            #a["value"] -= 0.1
            b["value"] += 1.0
            a["reputation"] = min(a["reputation"] + 1, max_reputation)

            self.last_relation = "cooperate"  # store for GUI

        else:  # agent defects
            a["value"] += 0.1
            a["reputation"] = max(a["reputation"] -1, min_reputation)

            self.last_relation = "defect"  # store for GUI

    def _update_log(self, generation = False):
        """adds the current values and reputations to the log"""
        if generation:
            for key in self.log:
                self.log[key].append([agent[key] for agent in self.agents])


from simulation_numpy import ValuePlot, ReputationPlot

class StrategyHistogram(Diagram):
    """A modified PlotWindow to display an updateable histogram"""
    key = "strategy distribution"
    window_title = "Distribution of Strategies"

    def plot(self):
        data = self.simulation.log[self.simulation.current_generation - 1]["strategy"]
        if len(data):
            self.subplot.cla()
            self.subplot.axis(xmin=-6, xmax=7)
            self.subplot.hist(data, range(-6, 8), color="green", align="left")
            self.subplot.set_xticks(range(-5, 7))

diagrams = [ ValuePlot, ReputationPlot, StrategyHistogram ]


