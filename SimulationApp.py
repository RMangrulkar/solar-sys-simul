import sys
import numpy as np
import random

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import * 
from PyQt6.QtGui import QFontMetrics

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qtagg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

import SolarSysClass as solar

class MatplotWindow(QMainWindow):
    '''
    Generates a window with a matplotlib plot of the solar system input
    '''
    def __init__(self,
                 solar_system,
                 interact):
        super().__init__()

        self._main = QWidget()
        self.setCentralWidget(self._main)
        self.interact = interact
        self.solar_system = solar_system
        self.canvas = FigureCanvas(self.solar_system.fig)
        
        layout = QVBoxLayout(self._main)
        layout.addWidget(NavigationToolbar(self.canvas, self))
        layout.addWidget(self.canvas)
        
        self.update()
        self.show()
       
        self.timer = QTimer()
        self.timer.setInterval(self.solar_system.delta_t)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def update(self):
        if self.interact == 'Y':
            self.solar_system.step()
        elif self.interact == 'N':
            self.solar_system.step_no_planet_interact()
        self.canvas.draw()
    
'''End class'''

class SimulationTab(QWidget):
    '''
    Class for the simulation window
    user is given options to:
    (a) Enter mass of the central star/planet
    (b) Enter number of revolving planets
    (c) Enter mass, position, velocity of planets
    (d) Enter the method: Euler, Leapfrog or Runge-Kutta
    '''
    def __init__(self):
        super().__init__()
        # Attributes for storing user inputs
        self.num_planets = 0
        self.mass_planets_asWidget = []
        self.pos_planets_asWidget = []
        self.vel_planets_asWidget = []
        self.default_method = "Euler"
        self.delta_t = 1
        '''
        The layout is:
        1. label and spinbox to get number of bodies
        2. Masses of bodies
        3. Positions of bodies
        4. Velocities of bodies
        '''
        label = QLabel("NUMBER OF BODIES (INCLUDING THE CENTRAL BODY):")
        
        self.spinBox = QSpinBox(self)
        self.spinBox.setRange(0,6)
        self.spinBox.valueChanged.connect(self.set_planet_info)

        self.apply_button = QPushButton("Apply", clicked = self.clicked_apply)
        self.generate_button = QPushButton("Generate", clicked = self.clicked_generate)
        self.save_button = QPushButton("Save", clicked=self.clicked_save)
        
        self.lineEdit = QLineEdit
        self.massBox = QGroupBox("Masses")
        self.mass_layout = QHBoxLayout(self.massBox)
        scroll_area1 = QScrollArea()
        scroll_area1.setWidgetResizable(True)
        scroll_area1.setWidget(self.massBox)

        posBox = QGroupBox("Positions")
        self.pos_layout = QVBoxLayout(posBox)
        scroll_area2 = QScrollArea()
        scroll_area2.setWidgetResizable(True)
        scroll_area2.setWidget(posBox)

        velBox = QGroupBox("Velocities")
        self.vel_layout = QVBoxLayout(velBox)
        scroll_area3 = QScrollArea()
        scroll_area3.setWidgetResizable(True)
        scroll_area3.setWidget(velBox)
        
        self.select_method = QComboBox()
        self.select_method.addItems(["Euler", "Leapfrog"])
        self.status_label = QLabel("READY")
        
        self.set_dT = QLineEdit()
        self.set_dT.setPlaceholderText("Time increment (integer)")

        g_layout = QGridLayout(self)
        g_layout.addWidget(label, 0, 0)
        g_layout.addWidget(self.spinBox, 0, 1)
        g_layout.addWidget(scroll_area1, 1, 0)
        g_layout.addWidget(scroll_area2, 2, 0)
        g_layout.addWidget(scroll_area3, 3, 0)
        g_layout.addWidget(self.select_method, 3, 1)
        g_layout.addWidget(self.set_dT, 3, 2)
        g_layout.addWidget(self.apply_button, 4, 0)
        g_layout.addWidget(self.generate_button, 4, 1)
        g_layout.addWidget(self.save_button, 4, 2)
        g_layout.addWidget(self.status_label, 5, 0)
        g_layout.setColumnStretch(5, 3)

    # When "Apply" is clicked the variable values are set
    def clicked_apply(self):
        # Attributes for storing processed info
        self.status('busy')
        self.masses = np.zeros(self.num_planets)
        self.positions = np.zeros((self.num_planets, 3))
        self.velocities = np.zeros((self.num_planets, 3))
        
        try:
            for i in range(self.num_planets):
                self.masses[i] = float(self.mass_planets_asWidget[i].text())
                for j in range(3):
                    self.positions[i][j] = float(self.pos_planets_asWidget[i][j].text())
                    self.velocities[i][j] = float(self.vel_planets_asWidget[i][j].text())
            self.status('normal') 
        except ValueError:
            self.status('error')


    # Clicking the "generate" button creates a new window with the matplotlib animation
    def clicked_generate(self):
        self.status('busy')
        self.default_method = self.select_method.currentText()

        try:
            check_valid_dT = int(self.set_dT.text())
            if check_valid_dT <= 0:
                raise ValueError
            self.delta_t = check_valid_dT
        except ValueError:
            self.status('error')

        self.solar_system = solar.SolarSys(method = self.default_method,
                                           delta_t = self.delta_t)
        planet_dict = {}
        for i in range(self.num_planets):
            key = 'planet'+str(i)
            if i == 0:
                planet_dict['key'] = solar.Sun(self.solar_system,
                                               mass = self.masses[i],
                                               position = self.positions[i],
                                               velocity = self.velocities[i])
            else:
                planet_dict['key'] = solar.Planet(self.solar_system,
                                                  mass = self.masses[i],
                                                  position = self.positions[i],
                                                  velocity = self.velocities[i])

        
        self.matplotwindow = MatplotWindow(solar_system = self.solar_system, interact='Y')
        self.matplotwindow.show()
        self.status('normal')

    def clicked_save(self):
        self.status('busy')
        self.default_method = self.select_method.currentText()

        try:
            check_valid_dT = int(self.set_dT.text())
            if check_valid_dT <= 0:
                raise ValueError
            self.delta_t = check_valid_dT
        except ValueError:
            self.status('error')

        self.solar_system = solar.SolarSys(self.default_method, delta_t = self.delta_t)
        planet_dict = {}
        for i in range(self.num_planets):
            key = 'planet'+str(i)
            if i == 0:
                planet_dict['key'] = solar.Sun(self.solar_system,
                                               mass = self.masses[i],
                                               position = self.positions[i],
                                               velocity = self.velocities[i])
            else:
                planet_dict['key'] = solar.Planet(self.solar_system,
                                                  mass = self.masses[i],
                                                  position = self.positions[i],
                                                  velocity = self.velocities[i])


        def animate(i):
            self.solar_system.step()
            self.solar_system.fix_axes()

        anim = animation.FuncAnimation(self.solar_system.fig, animate, frames=1200,
                                       interval=10)
        writervideo = animation.FFMpegWriter(fps=60)
        anim.save("simul.mp4", writer=writervideo, dpi = 600)
        self.status('normal')

    # From user input in self.spinBox set mass, position and velocity of planets
    def set_planet_info(self, input_value):
        self.set_planet_masses(input_value)
        self.set_planet_positions(input_value)
        self.set_planet_velocities(input_value)
        self.num_planets = input_value


    # Information of mass is displayed dynamically and stored as a widget
    def set_planet_masses(self, input_value):
        new_num = int(input_value)
        count = len(self.mass_planets_asWidget)

        for ii in range(count, new_num):
            mass = self.lineEdit(self)
            if ii == 0:
                mass.setPlaceholderText("Central body")
            else:
                mass.setPlaceholderText("Planet "+str(ii))
            mass.setFixedSize(mass.sizeHint())
            self.mass_planets_asWidget.append(mass)
            self.mass_layout.insertWidget(ii, mass, alignment=Qt.AlignmentFlag.AlignLeft)
        for ii in range(self.num_planets, new_num):
            self.mass_layout.itemAt(ii).widget().show()
        for ii in range(new_num, self.num_planets):
            self.mass_layout.itemAt(ii).widget().hide()

    # Same as set_planet_masses but 3 fields of position per planet
    def set_planet_positions(self, input_value):
        new_num = int(input_value)
        count = len(self.pos_planets_asWidget)
        for ii in range(count, new_num):
            # Each row has (x,y,z) info
            position = QHBoxLayout()
            if ii == 0:
                title = QLabel("Central body (enter all zeroes): ")
            else:
                title = QLabel("Planet "+str(ii))
            
            xlabel = self.lineEdit(self)
            xlabel.setPlaceholderText("x")
            ylabel = self.lineEdit(self)
            ylabel.setPlaceholderText("y")
            zlabel = self.lineEdit(self)
            zlabel.setPlaceholderText("z")
            position.addWidget(title, 0)
            position.addWidget(xlabel, 0)
            position.addWidget(ylabel, 0)
            position.addWidget(zlabel,0)
            position.addStretch()

            temp_array = [xlabel, ylabel, zlabel]
            self.pos_planets_asWidget.append(temp_array)
            pos_widget = QWidget()
            pos_widget.setLayout(position)
            self.pos_layout.insertWidget(ii, pos_widget)

        for ii in range(self.num_planets, new_num):
            self.pos_layout.itemAt(ii).widget().show()

        for ii in range(new_num, self.num_planets):
            self.pos_layout.itemAt(ii).widget().hide()
        
        
    # Same as set_planet_masses but 3 fields of velocity per planet
    def set_planet_velocities(self, input_value):
        new_num = int(input_value)
        count = len(self.vel_planets_asWidget)
        for ii in range(count, new_num):
            # Each row has (x,y,z) info
            velocity = QHBoxLayout()
            if ii == 0:
                title = QLabel("Central body (enter all zeroes): ")
            else:
                title = QLabel("Planet "+str(ii))
            
            xlabel = self.lineEdit(self)
            xlabel.setPlaceholderText("v_x")
            ylabel = self.lineEdit(self)
            ylabel.setPlaceholderText("v_y")
            zlabel = self.lineEdit(self)
            zlabel.setPlaceholderText("v_z")
            velocity.addWidget(title,  0)
            velocity.addWidget(xlabel, 0)
            velocity.addWidget(ylabel, 0)
            velocity.addWidget(zlabel, 0)
            velocity.addStretch()

            temp_array = [xlabel, ylabel, zlabel]
            self.vel_planets_asWidget.append(temp_array)
            pos_widget = QWidget()
            pos_widget.setLayout(velocity)
            self.vel_layout.insertWidget(ii, pos_widget)

        for ii in range(self.num_planets, new_num):
            self.vel_layout.itemAt(ii).widget().show()

        for ii in range(new_num, self.num_planets):
            self.vel_layout.itemAt(ii).widget().hide()


    def status(self, status):
        if status == 'normal':
            self.status_label.setText('READY')
        elif status == 'error':
            self.status_label.setText("Incomplete or incorrect data!")
        elif status == 'busy':
            self.status_label.setText("Busy")

'''End class'''

class VelocityTab(QWidget):
    '''
    Generates a collection of planets with randomised velocities
    '''
    def __init__(self):
        super().__init__()
        self.num_planets = 0
        self.centre_mass = 0
        self.planet_mass = 0
        self.planet_dist = 0
        self.planet_speed = 0


        self.num_title = QLabel("Number of trajectories to calculate:")
        self.title_central_mass = QLabel("Mass of central body:")
        self.title_planet_mass = QLabel("Mass of planet:")
        self.title_dist = QLabel("Distance:")
        self.title_speed = QLabel("Speed:")
        
        self.set_central_mass = QLineEdit()
        self.set_central_mass.setPlaceholderText("Mass of centre")
        self.set_planet_mass = QLineEdit()
        self.set_planet_mass.setPlaceholderText("Mass of planet")
        self.set_planet_dist = QLineEdit()
        self.set_planet_dist.setPlaceholderText("Distance")
        self.set_planet_speed = QLineEdit()
        self.set_planet_speed.setPlaceholderText("Speed")

        self.spinBox = QSpinBox(self)
        self.spinBox.setRange(1,10)
        self.spinBox.valueChanged.connect(self.set_planet_info)

        self.apply_button = QPushButton("Apply", clicked = self.clicked_apply)
        self.generate_button = QPushButton("Generate", clicked = self.clicked_generate)
        self.save_button = QPushButton("Save", clicked=self.clicked_save)

        self.select_method = QComboBox()
        self.select_method.addItems(["Euler", "Leapfrog"])
        self.status_label = QLabel("READY")
        
        self.set_dT = QLineEdit()
        self.set_dT.setPlaceholderText("Time increment (integer)")

        layout = QGridLayout(self)
        layout.addWidget(self.num_title, 0, 0)
        layout.addWidget(self.spinBox, 0, 1)
        layout.addWidget(self.title_central_mass, 1, 0)
        layout.addWidget(self.set_central_mass, 1, 1)
        layout.addWidget(self.title_planet_mass, 1, 2)
        layout.addWidget(self.set_planet_mass, 1, 3)
        layout.addWidget(self.title_dist, 2, 0)
        layout.addWidget(self.set_planet_dist, 2, 1)
        layout.addWidget(self.title_speed, 2, 2)
        layout.addWidget(self.set_planet_speed, 2, 3)
        layout.addWidget(self.set_dT, 3, 0)
        layout.addWidget(self.select_method, 3, 1)
        layout.addWidget(self.apply_button, 3, 2)
        layout.addWidget(self.generate_button, 3, 3)
        layout.addWidget(self.save_button, 4, 3)
        layout.addWidget(self.status_label, 4, 0)
        layout.setColumnStretch(4,3)
        layout.setRowStretch(5,1)

    def clicked_generate(self):
        self.status('busy')
        self.default_method = self.select_method.currentText()

        try:
            check_valid_dT = int(self.set_dT.text())
            if check_valid_dT <= 0:
                raise ValueError
            self.delta_t = check_valid_dT
        except ValueError:
            self.status('error')

        self.solar_system = solar.SolarSys(method = self.default_method,
                                           delta_t = self.delta_t)

        random_dict = {}
        sun = solar.Sun(self.solar_system,
                        mass = self.centre_mass,
                        position = np.zeros(3),
                        velocity = np.zeros(3))

        for i in range(self.num_planets):
            key = 'random'+str(i)
            theta = np.pi*random.random()
            phi = 2*np.pi*random.random()
            vel = self.planet_speed*np.array([np.sin(theta)*np.cos(phi),
                                              np.sin(theta)*np.sin(phi),
                                              np.cos(theta)])

            random_dict['key'] = solar.Planet(self.solar_system,
                                              mass = self.planet_mass,
                                              position = np.array([self.planet_dist, 0, 0]),
                                              velocity = vel)

        self.matplotwindow = MatplotWindow(solar_system = self.solar_system, interact='N')     
        self.matplotwindow.show()
        self.status('normal')


    def clicked_save(self):
        self.status('busy')
        self.default_method = self.select_method.currentText()

        try:
            check_valid_dT = int(self.set_dT.text())
            if check_valid_dT <= 0:
                raise ValueError
            self.delta_t = check_valid_dT
        except ValueError:
            self.status('error')

        self.solar_system = solar.SolarSys(method = self.default_method,
                                           delta_t = self.delta_t)

        random_dict = {}
        sun = solar.Sun(self.solar_system,
                        mass = self.centre_mass,
                        position = np.zeros(3),
                        velocity = np.zeros(3))

        for i in range(self.num_planets):
            key = 'random'+str(i)
            theta = np.pi*random.random()
            phi = 2*np.pi*random.random()
            vel = self.planet_speed*np.array([np.sin(theta)*np.cos(phi),
                                              np.sin(theta)*np.sin(phi),
                                              np.cos(theta)])

            random_dict['key'] = solar.Planet(self.solar_system,
                                              mass = self.planet_mass,
                                              position = np.array([self.planet_dist, 0, 0]),
                                              velocity = vel)

        def animate(i):
            self.solar_system.step_no_planet_interact()
            self.solar_system.fix_axes()

        anim = FuncAnimation(self.solar_system.fig, animate, frames=1200,
                             interval=10)
        writervideo = animation.FFMpegWriter(fps=60)
        anim.save("random.mp4", writer=writervideo, dpi = 600)


    def clicked_apply(self):
        self.status('busy')
        
        try:
            self.centre_mass = float(self.set_central_mass.text())
            self.planet_mass = float(self.set_planet_mass.text())
            self.planet_dist = float(self.set_planet_dist.text())
            self.planet_speed = float(self.set_planet_speed.text())
            
            self.status('normal')
        
        except ValueError:
            self.status('error')

    def set_planet_info(self, input_value):
        self.num_planets = input_value

    def status(self, status):
        if status == 'normal':
            self.status_label.setText('READY')
        elif status == 'error':
            self.status_label.setText("Incomplete or incorrect data!")
        elif status == 'busy':
            self.status_label.setText("Busy")
'''End class'''

class MainWindow(QMainWindow):
    '''Window that contains all functionality'''
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Preliminaries
        self.setWindowTitle("Solar System Simulation")
        self.setMinimumSize(QSize(800, 600))

        # Create tabs for different functions
        tabs = QTabWidget()
        tabs.setDocumentMode(False)
        simulation = SimulationTab()
        velocities = VelocityTab()
        tabs.addTab(simulation, "Simulation")
        tabs.addTab(velocities, "Random velocities")
        
        self.setCentralWidget(tabs)

'''End class'''


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
