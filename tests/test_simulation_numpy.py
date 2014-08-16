# -*- coding: utf-8 -*-

"""

"""
from unittest import TestCase

__author__ = 'joscha'
__date__ = '14.07.14'

from simulation_numpy import Simulation, Settings, FITNESS, AGENT

class TestSimulation(TestCase):
    def test___init__(self):
        s = Simulation()
        assert len(s.agents) == Settings.number_of_agents
        for a in s.agents:
            assert a["value"] == 0.0
            assert a["reputation"] == 0
            assert a["deception probability"] == 0.5
        assert s.current_simstep == 0
        assert s.current_generation == 1
        assert len(s.log) == Settings.number_of_generations
        assert len(s.log[0]) == Settings.number_of_agents
        assert len(s.log[0][0]) == len(AGENT)

    def test_step(self):
        s = Simulation()
        current_step = s.current_simstep
        current_generation = s.current_generation
        s.step()
        assert s.current_simstep == current_step + 1
        assert s.current_generation == current_generation
        # with default settings, one agent should have cooperated, and one received payoff
        number_of_payoffs = 0
        number_of_cost = 0
        number_of_negative_reputations = 0
        number_of_positive_reputations = 0
        for a in s.agents:
            if a["value"] == 1.0:
                number_of_payoffs += 1
                assert a["reputation"]==0. or a["reputation"]==-1.0
            elif a["value"] == -0.5:
                number_of_cost += 1
            else:
                assert a["value"] == 0.
            if a["reputation"] == -1.:
                number_of_negative_reputations += 1
            elif a["reputation"] == 1.:
                number_of_positive_reputations += 1
            else:
                assert a["reputation"] == 0
        assert number_of_payoffs == 1
        assert number_of_cost ==1
        assert number_of_positive_reputations == 0 or number_of_positive_reputations == 1
        assert number_of_negative_reputations == 0 or number_of_negative_reputations == 1

    def test_step_with_generation_change(self):
        s = Simulation()
        s.current_simstep = Settings.number_of_simulation_steps_in_a_generation
        current_generation = s.current_generation
        s.step()
        assert s.current_simstep == 0
        assert s.current_generation == current_generation +1
        for a in s.agents:
            assert a["value"] == 0.
            assert a["reputation"] == 0

    def test_step_without_deception(self):
        s = Simulation()
        s.agents["deception probability"] = 0.
        for i in range (0,100):
            s.step()
            for r in s.agents["reputation"]:
                assert r >= 0

    def test_step_with_deception(self):
        s = Simulation()
        s.agents["deception probability"] = 1.

        for i in range(0, 100):
            s.agents["reputation"] = 0
            s.step()
            number_of_negative_reputations = 0
            for r in s.agents["reputation"]:
                if r<0:
                    number_of_negative_reputations += 1
            assert number_of_negative_reputations == 2 or number_of_negative_reputations == 0 or \
                   number_of_negative_reputations == 1

