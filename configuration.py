# -*- coding: utf-8 -*-

"""
Config data (default values) for reputation game
"""

__author__ = 'joscha'
__date__ = '20.06.14'

APPTITLE = "Reputation Game with Evolving Deception"
VERSION = "0.1"

class Settings():
    number_of_agents = 20
    probability_of_a_reputation_exchange= 0.5
    probability_of_repercussion_for_reputation_diminishment=0.2
    number_of_simulation_steps_in_a_generation= 1000
    number_of_generations= 20
    number_of_surviving_agents= 0
    number_of_parents_in_a_generation= 5
    influence_of_fitness_to_reproductive_success= 0.0
    mutation_rate= 0.2
    update_rate_during_calculate_all = 1  # update gui display every n cycles during fast computation
