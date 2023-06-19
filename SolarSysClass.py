import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

class SolarSys():
    """This class contains all of the planets and their motion"""
    def __init__(self,
                 method,
                 delta_t):
        """Initialise the solar system"""
        self.delta_t = delta_t
        self.method = method
        self.planets = []
        self.lim = 500
        self.N_DIM = 3
        # Initialise the 3D axes
        self.fig = plt.figure(figsize=(12,9))
        self.ax = Axes3D(self.fig, auto_add_to_figure=False)
        self.fig.add_axes(self.ax)
    

    def step(self):
        if self.method == "Euler":
            for planet in self.planets:
                planet.update_position(self.delta_t)
            self.planet_interaction(self.delta_t)

        elif self.method == "Leapfrog":
            for planet in self.planets:
                planet.update_position(self.delta_t / 2)

            self.planet_interaction(self.delta_t)

            for planet in self.planets:
                planet.update_position(self.delta_t / 2)

        self.plot_planets()
    
    def step_no_planet_interact(self):
        if self.method == "Euler":
            for planet in self.planets:
                planet.update_position(self.delta_t)
            self.interaction_sun_only(self.delta_t)

        elif self.method == "Leapfrog":
            for planet in self.planets:
                planet.update_position(self.delta_t / 2)

            self.interaction_sun_only(self.delta_t)

            for planet in self.planets:
                planet.update_position(self.delta_t / 2)

        self.plot_planets()

    def add_planet(self, planet):
        """Add a new planet to the planets array"""
        self.planets.append(planet)

    def plot_planets(self):
        """Plot the planets on the solar system figure"""
        self.ax.clear()
        ang_textbox = "Angular Momenta:\n"
        energy_textbox = "Energies:\n"
        self.calc_qts()

        for i, planet in enumerate(self.planets):
            planet.add_to_plot()
            if not(isinstance(planet, Sun)):
                planet.add_velocity_marker()
                self.ax.text(planet.position[0], planet.position[1], planet.position[2],
                             f"{i}", zorder=10)

                with np.printoptions(precision=2):
                    ang_textbox += f"Planet {i}: {planet.ang_moment}\n"
                energy_textbox += (f"Planet {i}: "+
                                   f" K = {planet.kinetic_energy:.2f}"+
                                   f" P = {planet.pot_energy:.2f}"+
                                   f" Total = {planet.tot_energy:.2f}\n")
        
        self.ax.text2D(0.85, 0.85, ang_textbox, fontsize = 6, transform = self.ax.transAxes)
        self.ax.text2D(-0.3, 0.85, energy_textbox, fontsize = 6, transform = self.ax.transAxes)
        self.fix_axes()


    def fix_axes(self):
        """Keep the axis limits constant"""
        self.ax.set_xlim(-self.lim, self.lim)
        self.ax.set_ylim(-self.lim, self.lim)
        self.ax.set_zlim(-self.lim, self.lim)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.grid(False)


    def planet_interaction(self, dT):
        """Uses the gravity method to find the net interactions"""
        for i, first in enumerate(self.planets):
            for j, second in enumerate(self.planets):
                if i != j:
                    first.gravity(second, dT)

    def interaction_sun_only(self, dT):
        sun_index = 0
        for i, planet in enumerate(self.planets):
            if isinstance(planet, Sun):
                sun_index = i
        for i, planet in enumerate(self.planets):
            if i != sun_index:
                planet.gravity(self.planets[sun_index], dT)

    def calc_qts(self):
        for i, first in enumerate(self.planets):
            if not(isinstance(first, Sun)):
                first.ang_moment = np.cross(first.position, first.velocity)
                first.kinetic_energy = 0.5*first.mass*(np.linalg.norm(first.velocity))**2
                first.pot_energy = 0
                for j, second in enumerate(self.planets):
                    if i != j:
                        rel_vec = np.subtract(second.position, first.position)
                        first.pot_energy -= (first.mass * second.mass) / np.linalg.norm(rel_vec)
                first.tot_energy = first.pot_energy + first.kinetic_energy
'''End class'''


class Planet():
    """This class creates planets/stars and defines their properties"""
    def __init__(
            self, 
            SolarSys, 
            mass,
            position = np.zeros(3),
            velocity = np.zeros(3),
        ):
        self.SolarSys = SolarSys
        self.mass = mass
        self.velocity = velocity
        self.position = position
        # Auto-add-to solar system 
        self.SolarSys.add_planet(self)
        self.color = 'black'
        self.mksize = 3
        self.ang_moment = np.zeros(3)
        self.tot_energy = 0
        self.kinetic_energy = 0
        self.pot_energy = 0

    def add_to_plot(self):
        """Add the planet to the figure"""
        self.SolarSys.ax.plot(*self.position, marker='o', markersize=self.mksize,  
                              color=self.color)

    def add_velocity_marker(self):
        '''Add a velocity vector from the planet'''
        final = np.add(self.position, 15*self.velocity)
        self.SolarSys.ax.plot([self.position[0],final[0]],[self.position[1],final[1]], 
                              [self.position[2],final[2]], color='red', linewidth=0.8)

    # Additional parameter of dT to accommodate Euler and Leapfrog methods
    def update_position(self, dT):
        """New position = old position + velocity*time"""
        self.position += self.velocity*dT

    def gravity(self, other, dT):
        """Calculates the gravitational acceleration on self due to other"""
        relative_pos = np.subtract(other.position, self.position)
        distance = np.linalg.norm(relative_pos)
        direction = np.divide(relative_pos, distance)
        acc_self = (other.mass/distance**2)*direction
        self.velocity += acc_self*dT

class Sun(Planet):
    """Identical to planet except it is fixed at origin"""
    def __init__(
            self,
            SolarSys,
            mass = 1000,
            position = np.zeros(3),
            velocity = np.zeros(3),
            ):
        super(Sun, self).__init__(SolarSys, mass, position, velocity)
        self.color = 'yellow'
        self.mksize = 10

    def update_position(self, dT):
        """Position is unchanged"""
        self.position = self.position
'''End class'''
