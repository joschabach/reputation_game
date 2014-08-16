# -*- coding: utf-8 -*-

"""
Definition of agents and simulation function
"""

__author__ = 'joscha'
__date__ = '20.06.14'

from random import randint, random
import numpy as np

from widgets import Settings
from helper_widgets import Diagram


def cooperation_policy(agent, other_agent):
    """Return true to cooperate, false to defect"""
    return other_agent["reputation"] >= 0


def reputation_policy(agent, other_agent):
    """Return true to diminish reputation, false otherwise"""
    return random() < agent["deception probability"]


#fitness = lambda agent: agent["value"]  # fitness function used in selecting agents


FITNESS = "value"  # should be a column in the agent's dtype

#AGENT = [("value", float), ("reputation", int), ("deception probability", float)]

class Simulation(object):
    def __init__(self):

        self.init_agents()

        self.current_simstep = 0
        self.current_generation = 1

        self.last_relation = None
        self.last_agent_0_index = None
        self.last_agent_1_index = None

        self.log = np.zeros((Settings.number_of_generations+1, Settings.number_of_agents), dtype = self.agents.dtype)
        self.log[self.current_generation] = self.agents

    def init_agents(self):
        self.agents = np.zeros(Settings.number_of_agents, dtype = [("value", float), ("reputation", int), ("deception probability", float)])
        self.agents["deception probability"] = 0.5


    def step(self):
        """Advances the simulation by a single step. Returns False if we are done"""
        if self.current_simstep < Settings.number_of_simulation_steps_in_a_generation:
            self.cooperation_step()
            self.deception_step()
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


    def calculate_generation(self):
        """Advances the simulation by a generation"""
        this_generation = self.current_generation
        if this_generation <= Settings.number_of_generations:
            while self.current_generation == this_generation and self.step():
                pass


    def select_agents(self):
        """At the end of every generation, the game goes into a new round.
        Some of the most successful agents may be allowed to carry on (with values and reputations being reset).
        Among the successful agents, parents for the next generation are chosen.
        The next generation's decision parameter is mutated by mutation_rate * random().
        The idea is that over time, the simulation may approach an optimal decision parameter.
        """

        # sort agents by fitness

        #self.agents.sort(key=fitness, reverse=True)

        agents = self.agents[self.agents[FITNESS].argsort()][::-1]

        # identify future parents (the currently fittest agents)
        parents = agents[:Settings.number_of_parents_in_a_generation]

        # normalize fitness values between 1 and 0:
        # we assume that the worst agent of the current generation has a fitness of 0, and the best of 1
        min_fitness, max_fitness = agents[FITNESS][[-1, 0]]
        if (max_fitness > min_fitness):
            norm_factor = 1 / (max_fitness - min_fitness)
        else:
            norm_factor = 0

        # determine ratios of children among parents
        normalized_fitness = norm_factor * (parents[FITNESS] - min_fitness)
        shares = (1- Settings.influence_of_fitness_to_reproductive_success) + \
                 normalized_fitness * Settings.influence_of_fitness_to_reproductive_success

        # carry over survivors, these won't be mutated (but the relevant value is copied)
        self.agents[:Settings.number_of_surviving_agents] = agents[:Settings.number_of_surviving_agents]


        # create children
        number_of_children = Settings.number_of_agents-Settings.number_of_surviving_agents
        m = number_of_children/np.sum(shares)
        number_of_children_of_agent = np.ceil(m * shares).astype(int)
        self.agents[Settings.number_of_surviving_agents:] = np.repeat(parents,
                                                                      number_of_children_of_agent)[:number_of_children]
        self.mutate_agents(self.agents[Settings.number_of_surviving_agents:])

        self.reset_agents(self.agents)


    def mutate_agents(self, agents):
        """called for the array of children of a new generation"""
        np.clip(np.random.uniform(-Settings.mutation_rate, Settings.mutation_rate, size=len(agents)) +
                agents["deception probability"], 0.0, 1.0, out=agents["deception probability"])

    def reset_agents(self, agents):
        """reset agent parameters at the start of a new generation"""
        agents["value"] = 0
        agents["reputation"] = 0


    def cooperation_step(self):

        a, b = self._get_two_agents()

        cooperation = cooperation_policy(a, b)
        if cooperation:  # agent cooperates
            a["value"] -= 0.5
            b["value"] += 1.0
            a["reputation"] = min(a["reputation"] + 1, 5)

            self.last_relation = "cooperate"  # store for GUI

        else:  # agent defects
            a["reputation"] = max(a["reputation"] - 1, -5)

            self.last_relation = "defect"  # store for GUI


    def deception_step(self, display_steps=True):
        if random() < Settings.probability_of_a_reputation_exchange:
            return

        a, b = self._get_two_agents()

        reputation_diminishment = reputation_policy(a, b)
        if reputation_diminishment:  # agent badmouths the other agent
            b["reputation"] = max(b["reputation"] - 1.0, -5)
            if random() < Settings.probability_of_repercussion_for_reputation_diminishment:
                a["reputation"] = max(a["reputation"] - 1.0, -5)
                self.last_relation = "deception"  # store for GUI


    def _get_two_agents(self):
        """Select two agents randomly"""
        self.last_agent_0_index, self.last_agent_1_index = np.random.choice(Settings.number_of_agents, 2, replace=False)
        return self.agents[self.last_agent_0_index], self.agents[self.last_agent_0_index]



class ValuePlot(Diagram):
    key = "value"
    window_title = " Average payoffs"

    def plot(self):
        data = self.simulation.log[:self.simulation.current_generation]["value"]
        if len(data)>1:
            self.subplot.cla()
            self.subplot.plot(data.mean(axis = 1), color = "orange", linewidth =1.0)

class ReputationPlot(Diagram):
    key = "reputation"
    window_title = " Average reputation"

    def plot(self):
        data = self.simulation.log[:self.simulation.current_generation][self.key]
        if len(data):
            self.subplot.cla()
            self.subplot.plot(data.mean(axis=1), color="blue", linewidth=1.0)



class DeceptionPlot(Diagram):
    key = "deception probability"
    window_title = " Average probability of deception"

    def plot(self):
        data = self.simulation.log[:self.simulation.current_generation][self.key]
        if len(data):
            self.subplot.cla()
            self.subplot.plot(data.mean(axis=1), color="brown", linewidth=1.0)


class ValueHistogram(Diagram):
    """A modified PlotWindow to display an updateable histogram"""
    key = "payoff distribution"
    window_title = "Distribution of Payoffs"

    def plot(self):
        data = self.simulation.log[self.simulation.current_generation - 1]["value"]
        if len(data):
            self.subplot.cla()
            self.subplot.hist(data, bins=10, color="blue")


class DeceptionHistogram(Diagram):
    """A modified PlotWindow to display an updateable histogram"""
    key = "deception distribution"
    window_title = "Distribution of Deception probability"

    def plot(self):
        data = self.simulation.log[self.simulation.current_generation-1]["deception probability"]
        if len(data):
            self.subplot.cla()
            self.subplot.axis(xmin=0, xmax=1)
            self.subplot.hist(data, bins=10, color="brown")


diagrams = [ValuePlot, ReputationPlot, DeceptionPlot, ValueHistogram, DeceptionHistogram]


