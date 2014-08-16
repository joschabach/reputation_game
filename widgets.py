# -*- coding: utf-8 -*-

"""
Tkinter UI definition
"""

__author__ = 'joscha'
__date__ = '19.06.14'

from tkinter import *
from tkinter import ttk, filedialog, messagebox
from configuration import Settings
import math


#import simulation_numpy as simulation
import experiment_3 as simulation




from helper_widgets import MainMenu, SimFrame, ConfigDialog

class GuiApp(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        #self.geometry("500x500")
        self.minsize(500, 250)

        # menus
        self.option_add('*tearOff', FALSE)
        menubar = MainMenu(self)
        for diagram in simulation.diagrams:
            key = diagram.key
            menubar.menu_plot.add_command(label= "Plot " + key, command=lambda key=key : self.open_diagram(key))
        self.config(menu=menubar)

        # diagram
        self.open_diagrams = {}

        # frames
        content_frame = ttk.Frame(self)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        content_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        self.simulator = SimFrame(content_frame)
        self.simulator.grid(row=0, column=0, sticky=(W, E))


        spacer = ttk.Frame(content_frame)
        spacer.grid(row=98, column=0, sticky=(W, E, N, S))
        spacer.rowconfigure(0, weight=1)

        self.spacer = spacer

        self.status = StringVar()
        self.status_bar = ttk.Frame(content_frame, padding = (6, 6, 6, 6), relief="sunken")
        self.status_bar.grid(row=99, column=0, sticky=(W, E, N, S))
        self.status_label = ttk.Label(self.status_bar, textvariable = self.status)
        self.status_label.grid(row=0, column=0, sticky=(W, E, N, S))

        # simulation thread
        self.running = False
        self.gen_running = False

        self.reset_simulation()


    def open_diagram(self, key):
        """open a diagram window for the given type"""
        if not key in self.open_diagrams:
            for Diagram in simulation.diagrams:
                if Diagram.key == key:
                    self.open_diagrams[key] = Diagram(self, self.simulation)


    def calculate_agent_coordinates(self, agents):
        """Arrange the agents in a circle on the canvas"""
        self.agent_coordinates = []
        origin = (350, 350)
        r = 300
        k = len(agents)
        for n in range(0, k):
            self.agent_coordinates.append(
                (r * math.cos(2 * math.pi * n / k) + origin[0],
                 r * math.sin(2 * math.pi * n / k) + origin[1])
            )


    def configure_simulation(self):
        """Configure simulation settings and initialize values"""
        ConfigDialog(self)  # will call reset simulation for us

    def run_simulation(self):
        """Starts a runner that will trigger simulation steps"""
        self.status.set("running")
        self.running = True
        self.gen_running = False
        while self.running:
            self.simulation.step()
            self.update_display_after_simstep()
            self.update()

    def stop_simulation(self):
        """Pauses the runner that triggers simulation steps"""
        self.running = False
        if self.gen_running:
            self.gen_running = False
            self.update_after_generation()
        else:
            self.update_display_after_simstep()
        self.status.set("paused")

    def reset_simulation(self):
        """Initializes all values to original settings and sets up the canvas"""

        self.running = False
        self.gen_running = False

        self.simulation = simulation.Simulation()  # the self parameter tells the sim where to find the gui

        diagrams = list(self.open_diagrams.values())
        for plot in diagrams:
            plot.destroy()  # close diagrams because they are bound to old data sets

        self.setup_agent_drawings(self.simulation.agents)

        self.update_after_generation()
        self.status.set("ready to start")


    def step_simulation(self):
        """Advances the simulation by a single step"""
        self.running = False
        self.gen_running = False
        self.status.set("step")
        self.simulation.step()
        self.update_display_after_simstep()
        self.status.set("paused")

    def advance_one_generation(self):
        """Advances the simulation by a full generation"""
        self.running = False
        self.gen_running = False
        self.status.set("calculating...")
        self.update()
        self.simulation.calculate_generation()
        self.update_after_generation()
        self.status.set("paused")

    def calculate_all(self):
        """Perform the complete calculation"""
        self.running = False
        self.gen_running = True
        self.status.set("calculating...")
        while self.simulation.current_generation < Settings.number_of_generations and self.gen_running:
            self.simulation.calculate_generation()
            if self.simulation.current_generation % Settings.update_rate_during_calculate_all == 0:
                self.update()
                self.update_after_generation()
        self.update_after_generation()
        self.status.set("paused")

    def export_simulation_data(self):
        filename = filedialog.asksaveasfilename()
        print("export simulation "+filename)

    def export_plot(self):
        print("export diagram")

    def show_contact(self):
        messagebox.showinfo(title="Contact", message="Joscha Bach, 2014\njoscha@mit.edu")

    def setup_agent_drawings(self, agents):
        """Draw agents and their reputation values"""
        c = self.simulator.canvas
        self.calculate_agent_coordinates(agents)
        self.simulator.canvas.delete(ALL)
        radius = 10
        offset = 18
        self.agent_drawings = []
        self.agent_value_labels = []


        for i, (x, y) in enumerate(self.agent_coordinates):
            self.agent_drawings.append(c.create_oval(x-radius, y-radius, x+radius, y+radius,
                                                                         outline="black", fill="lightblue", width=2))
            self.agent_value_labels.append([
                c.create_text(x, y + offset, text="", fill="orange"),
                c.create_text(x, y + 2 * offset, text="", fill="blue"),
                c.create_text(x, y - offset, text="", fill="brown"),
                c.create_text(x, y - 2 * offset, text="", fill="green")])

        self.current_relation = None  # no line is drawn between agent images

    def update_agent_value_labels(self, agent_index, values):
        """paints the updated values on the canvas"""
        if isinstance(values, dict):
            values = [values["value"], values["reputation"], values["deception_probability"]]
        for index, value in enumerate(values):
            self.simulator.canvas.itemconfig(self.agent_value_labels[agent_index][index], text= str(round(value, 3)))

    def draw_relation(self, agent_index1, agent_index2, relation=None):
        """draws a visible link between two agents, of type "defect" or "cooperate".
        the line index is then stored in self.current_relation, so that it can be deleted later"""
        if agent_index1 is None or agent_index2 is None:
            self.delete_current_relation()
            return
        if relation is "defect":
            color = "red"
        elif relation is "cooperate":
            color = "green"
        else:
            color = "black"

        if self.current_relation:
            self.simulator.canvas.coords(self.current_relation,
                                         self.agent_coordinates[agent_index1][0],
                                         self.agent_coordinates[agent_index1][1],
                                         self.agent_coordinates[agent_index2][0],
                                         self.agent_coordinates[agent_index2][1])
            self.simulator.canvas.itemconfig(self.current_relation, fill=color, width=2)
        else:
            self.current_relation = self.simulator.canvas.create_line(self.agent_coordinates[agent_index1],
                                                 self.agent_coordinates[agent_index2],
                                                 arrow = "last", fill = color, width=2)

    def delete_current_relation(self):
        """removes the currently drawn line on the canvas, if there is one"""
        if self.current_relation:
            self.simulator.canvas.delete(self.current_relation)
            self.current_relation = None


    def update_display_after_simstep(self):
        """Update gui display after every individual simulationstep"""
        self.simulator.simstep.set(self.simulation.current_simstep)
        if self.simulation.last_relation:
            self.draw_relation(self.simulation.last_agent_0_index,
                               self.simulation.last_agent_1_index,
                               self.simulation.last_relation)
        else:
            self.delete_current_relation()
        if self.simulation.last_agent_0_index is not None:
            self.update_agent_value_labels(self.simulation.last_agent_0_index,
                                           self.simulation.agents[self.simulation.last_agent_0_index])
            self.update_agent_value_labels(self.simulation.last_agent_1_index,
                                           self.simulation.agents[self.simulation.last_agent_1_index])
        else:
            for i, a in enumerate(self.simulation.agents):
                self.update_agent_value_labels(i, a)


    def update_after_generation(self):
        """Update gui display after a generation has passed"""
        self.delete_current_relation()
        self.simulator.simstep.set(self.simulation.current_simstep)
        self.simulator.generation.set(self.simulation.current_generation)
        for i, a in enumerate(self.simulation.agents):
            self.update_agent_value_labels(i, a)
        self.update_plots()


    def update_plots(self):
        try:
            for plot in self.open_diagrams.values():
                plot.update_diagram()
        except RuntimeError:  # thread hates it when we add new diagrams while running
            pass

