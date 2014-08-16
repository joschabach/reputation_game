# -*- coding: utf-8 -*-

"""
Definition of agents and simulation function
"""

__author__ = 'joscha'
__date__ = '20.06.14'

from random import randint, random
import math

from widgets import Settings
from helper_widgets import Diagram

ereiam


def cooperation_policy(agent, other_agent):
    """Return true to cooperate, false to defect"""
    return other_agent["reputation"] >= 0


def reputation_policy(agent, other_agent):
    """Return true to diminish reputation, false otherwise"""
    return random() < agent["deception_probability"]


fitness = lambda agent: agent["value"]  # fitness function used in selecting agents


class Simulation(object):
    def __init__(self):

        self.agents = [self.create_agent() for x in range(0, Settings.number_of_agents)]


        self.current_simstep = 0
        self.current_generation = 1

        self.last_relation = None
        self.last_agent_0_index = None
        self.last_agent_1_index = None

        self.log = {key: [] for key in self.create_agent()}  # initialize an array for each agent property

    def create_agent(self):
        return {"value": 0,
                "reputation": 0,
                "deception_probability": 0}

    def step(self):
        """Advances the simulation by a single step. Returns False if we are done"""
        if self.current_simstep < Settings.number_of_simulation_steps_in_a_generation:
            self.cooperation_step()
            self.deception_step()
            self.current_simstep += 1
            self._update_log()
            return True
        else:
            if self.current_generation < Settings.number_of_generations:
                self._update_log(generation = True)
                self.last_relation = None
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
        self.agents.sort(key=fitness, reverse=True)

        # identify future parents (the currently fittest agents)
        parents = self.agents[:Settings.number_of_parents_in_a_generation]

        # normalize fitness values between 1 and 0:
        # we assume that the worst agent of the current generation has a fitness of 0, and the best of 1
        min_fitness = fitness(self.agents[-1])
        max_fitness = fitness(parents[0])
        if (max_fitness > min_fitness):
            norm_factor = 1 / (max_fitness - min_fitness)
        else:
            norm_factor = 0

        # determine ratios of children among parents
        shares = []
        sum_of_shares = 0
        for agent in parents:
            normalized_fitness = norm_factor * (fitness(agent) - min_fitness)
            share = (1 - Settings.influence_of_fitness_to_reproductive_success) + \
                    normalized_fitness * Settings.influence_of_fitness_to_reproductive_success
            sum_of_shares += share
            shares.append(share)

        # carry over survivors
        new_agents = self.agents[:Settings.number_of_surviving_agents]
        for agent in new_agents:  # reset agent's successes
            self.reset(agent)

        # create children
        new_children_born = len(self.agents) - len(new_agents)
        for index, agent in enumerate(parents):
            number_of_children_of_agent = math.ceil(new_children_born * shares[index] / sum_of_shares)
            for i in range(0, number_of_children_of_agent):
                if len(new_agents) < len(self.agents):
                    child = dict(agent)
                    self.reset(child)
                    self.mutate(child)
                    new_agents.append(child)
        self.agents = new_agents

    def mutate(self, agent):
        """called for each new agent that is born into a new generation"""
        agent["deception_probability"] = min(1.0, max(0.0, (Settings.mutation_rate * (2 * random() - 1) +
                                                            agent["deception_probability"])))

    def reset(self, agent):
        """determines which values should be reset at the end of a generation"""
        agent["reputation"] = 0
        agent["value"] = 0

    def cooperation_step(self, display_steps=True):
        self.last_agent_0_index, self.last_agent_1_index = self._get_two_agent_indices()
        a, b = self.agents[self.last_agent_0_index], self.agents[self.last_agent_1_index]

        cooperation = cooperation_policy(a, b)
        if cooperation:  # agent cooperates
            a["value"] -= 0.5
            b["value"] += 1.0
            a["reputation"] = min(a["reputation"] + 1, 5)

            self.last_relation = "cooperate"

        else:  # agent defects
            a["reputation"] = max(a["reputation"] - 1, -5)

            self.last_relation = "defect"


    def deception_step(self, display_steps=True):
        if random() < Settings.probability_of_a_reputation_exchange:
            return

        self.last_agent_0_index, self.last_agent_1_index = self._get_two_agent_indices()
        a, b = self.agents[self.last_agent_0_index], self.agents[self.last_agent_1_index]

        reputation_diminishment = reputation_policy(a, b)
        if reputation_diminishment:  # agent badmouths the other agent
            b["reputation"] = max(b["reputation"] - 1.0, -5)

            if random() < Settings.probability_of_repercussion_for_reputation_diminishment:
                a["reputation"] = max(a["reputation"] - 1.0, -5)

            self.last_relation = "deception"


    def _get_two_agent_indices(self):
        a = randint(0, len(self.agents) - 1)
        b = randint(0, len(self.agents) - 2)
        if b >= a:  # make sure that we do not choose the same agent twice
            b += 1
        return a, b

    def _update_log(self, generation = False):
        """adds the current values and reputations to the log.
        The generation parameter should be true if the call happens after a generation start"""
        for key in self.log:
            self.log[key].append([agent[key] for agent in self.agents])


class ValuePlot(Diagram):
    key = "value"
    window_title = "Values"


class ReputationPlot(Diagram):
    key = "reputation"
    window_title = "Reputation"

    def plot(self):
        data = self.simulation.log["reputation"]
        if len(data):
            values = [step[0] for step in data]
            self.subplot.plot(values, color="blue", linewidth=1.0)


class DeceptionPlot(Diagram):
    key = "deception probability"
    window_title = "Probability of Deception"

    def plot(self):
        data = self.simulation.log["deception probability"]
        if len(data):
            values = [step[0] for step in data]
            self.subplot.plot(values, color="brown", linewidth=1.0)


class ValueHistogram(Diagram):
    """A modified PlotWindow to display an updateable histogram"""
    key = "value distribution"
    window_title = "Distribution of Values"

    def plot(self):
        data = self.simulation.log["value"]
        self.subplot.cla()
        if len(data):
            values = [entry for entry in data[-1]]
            self.subplot.hist(values, bins=10, color="blue")


class DeceptionHistogram(Diagram):
    """A modified PlotWindow to display an updateable histogram"""
    key = "deception distribution"
    window_title = "Distribution of Deception probability"

    def plot(self):
        data = self.simulation.log["deception_probability"]
        self.subplot.cla()
        if len(data):
            self.subplot.axis(xmin=-6, xmax=7)
            values = [entry for entry in data[-1]]
            self.subplot.hist(values, bins=10, color="brown")


diagrams = [ValuePlot, ReputationPlot, DeceptionPlot, ValueHistogram, DeceptionHistogram]


