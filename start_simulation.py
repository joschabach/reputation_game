# -*- coding: utf-8 -*-

"""
Starts a gui with a simulation of a set of agents that play for cooperation and defect, maintain reputation and
may perform exchanges about each others reputations.

The agent strategies may be subject to an evolution.

TODO:
1. GUI framework
2. Define agents with policies and parameters
3. Define global parameters:
    - number of agents
    - alpha determines the probability of a reputation exchange
    - beta the probability of repercussions for the reputation diminisher
    - number of simulation steps in a generation
    - number of generations
    - number of surviving agents
    - number of parents in a generation
    - ratio of reputation to reproductive success
    - mutation factor
4. Define simulation step:
    - a selection function pairs agents for the interaction game
    - the agents decide to either cooperate or defect, using the cooperation strategy function (based on reputation)
    - the result is reflected in the reputation of the individual agents (which amounts to globally broadcasting it)
    - with probability alpha, an agent is asked if it wants to decrease the reputation of another agent, which may
      have repercussions
5. Define evolution step:
    - after n steps, choose the m fittest parents
    - number of children is number of agents - surviving agents
    - distribute children among parents according to approximate normalized reputation ratios
    - mutate children
6. Graphical display:
    - show agents in a circle
    - show interactions
    - update reputation scores
    - show global data (step, generation)
    - play, pause, step
    - illustrate generation switch
7. Plotting:
    - log all values into a file, annotated with time of simulation
    - draw a diagram

"""


__author__ = 'joscha'
__date__ = '19.06.14'

from configuration import APPTITLE, VERSION

import argparse
from widgets import GuiApp


def main():
    app = GuiApp()
    app.title("%s v%s" % (APPTITLE, VERSION))

    # put tkinter windows on top on macos
    app.lift()
    app.call('wm', 'attributes', '.', '-topmost', True)
    app.after_idle(app.call, 'wm', 'attributes', '.', '-topmost', False)

    app.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the %s desktop app." % APPTITLE)
    args = parser.parse_args()
    main()


