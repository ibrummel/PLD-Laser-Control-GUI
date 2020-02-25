# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:01:53 2019

@author: Ian
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDockWidget, QAction, QFileDialog, QMessageBox)
import sys
from Laser_Hardware import CompexLaser
from RPi_Hardware import RPiHardware
from Arduino_Hardware import LaserBrainArduino
from Docked_Motor_Control import MotorControlPanel
from Docked_Laser_Status_Control import LaserStatusControl
from Deposition_Control import DepControlBox
from Instrument_Preferences import InstrumentPreferencesDialog
from pathlib import Path
import os
import xml.etree.ElementTree as ET


class PLDMainWindow(QMainWindow):

    def __init__(self, laser: CompexLaser, brain: RPiHardware):
        super().__init__()
        self.menus = {}
        self.menu_actions = {}
        self.laser = laser
        self.brain = brain
        self.settings = InstrumentPreferencesDialog()
        self.loaded_deposition_path = None

        # Create a docked widget to hold the LSC module
        self.lsc_docked = LaserStatusControl(self.laser, self.brain)
        self.motor_control_docked = MotorControlPanel(self.brain)
        self.dep_control = DepControlBox(self.laser, self.brain, self)
        self.init_ui()

    def init_ui(self):
        self.setObjectName('Main Window')
        self.setWindowTitle('PLD Laser Control')
        self.setCentralWidget(self.dep_control)

        # self.lsc_docked.setWidget(LaserStatusControl(self.laser, self.brain))
        self.lsc_docked.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        # self.motor_control_docked.setWidget(MotorControlPanel(self.brain))
        self.motor_control_docked.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        self.setCorner(Qt.TopLeftCorner | Qt.TopRightCorner, Qt.TopDockWidgetArea)
        self.setCorner(Qt.BottomLeftCorner | Qt.BottomRightCorner, Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.TopDockWidgetArea, self.lsc_docked)
        self.addDockWidget(Qt.TopDockWidgetArea, self.motor_control_docked)
        self.tabifyDockWidget(self.lsc_docked, self.motor_control_docked)
        self.lsc_docked.raise_()

        self.init_menubar()

    def init_menubar(self):
        # Retrieve the menubar widget
        menubar = self.menuBar()

        # Create the file mennu
        file = menubar.addMenu('&File')
        # Create file actions
        file_load = self.build_menu_action('Load Deposition...', self.load_deposition, 'Ctrl+O')
        file_save = self.build_menu_action('Save Deposition', lambda: self.save_deposition(saveas=False), 'Ctrl+S')
        file_save_as = self.build_menu_action('Save Deposition As...', lambda: self.save_deposition(saveas=False),
                                              'Ctrl+Shift+S')
        file_new = self.build_menu_action('New Deposition', self.new_deposition, 'Ctrl+N')
        file_exit = self.build_menu_action('Exit', sys.exit, 'Ctrl+Q')
        file.addActions([file_load, file_save, file_save_as, file_exit])

        # Create the edit menu
        edit = menubar.addMenu('&Edit')
        # Create edit actions
        edit_preferences = self.build_menu_action('Preferences...', self.open_preferences, 'Ctrl+Alt+P')
        edit.addAction(edit_preferences)

    def build_menu_action(self, actstr, connection, shortcutstr=None):
        action = QAction(actstr, self)
        action.triggered.connect(connection)
        if shortcutstr is not None:
            action.setShortcut(shortcutstr)

        return action

    def open_preferences(self):
        self.settings.open()

    def load_deposition(self):
        # If the user has not loaded a file this session open home
        if self.loaded_deposition_path is None:
            load_file = QFileDialog.getOpenFileName(self, 'Select a deposition file to load...',
                                                    str(Path(os.path.expanduser('~'))),
                                                    'Deposition Files (*.depo);;XML Files (*.xml)')
        # If the user has loaded a file, attempt to open its directory
        else:
            try:
                load_file = QFileDialog.getOpenFileName(self, 'Select a deposition file to load...',
                                                        str(self.loaded_deposition_path),
                                                        'Deposition Files (*.depo);;XML Files (*.xml)')
            # if that doesn't work,
            except TypeError as err:
                print(err)
                self.loaded_deposition_path = None
                self.load_deposition()

        deposition = ET.parse(load_file[0])
        self.dep_control.load_xml_dep(deposition)
        self.loaded_deposition_path = Path(load_file[0])

    def save_deposition(self, saveas=True):
        deposition = self.dep_control.get_dep_xml()

        if not saveas and self.loaded_deposition_path is not None:
            save_file = self.loaded_deposition_path
        elif saveas and self.loaded_deposition_path is not None:
            save_file = QFileDialog.getSaveFileName(self, 'Select a Save Location...', str(self.loaded_deposition_path),
                                                    'Deposition Files (*.depo);;XML Files (*.xml)')
        else:
            save_file = QFileDialog.getSaveFileName(self, 'Select a Save Location...',
                                                    str(Path(os.path.expanduser('~'))),
                                                    'Deposition Files (*.depo);;XML Files (*.xml)')

        deposition_tree = ET.ElementTree(deposition)
        deposition_tree.write(self.return_file_dialogue_path(save_file))

    def new_deposition(self):
        if self.loaded_deposition_path is not None:
            clear_current_dep = QMessageBox.question(self, 'New Deposition',
                                                     'Staring a new deposition will clear previous work, would you\n'
                                                     ' like to save the current deposition before continuing?',
                                                     QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel,
                                                     QMessageBox.Save)
            if clear_current_dep == QMessageBox.Save:
                self.save_deposition(saveas=True)
                self.loaded_deposition_path = None
                self.new_deposition()
            elif clear_current_dep == QMessageBox.Discard:
                self.loaded_deposition_path = None
                self.new_deposition()
            elif clear_current_dep == QMessageBox.Cancel:
                return

        self.dep_control.clear_deposition()

    def return_file_dialogue_path(self, file_dialogue_return: tuple):
        path_obj = Path(file_dialogue_return[0])
        extension_str = file_dialogue_return[1].split('(')[1].split(')')[0].strip('*')

        if path_obj.suffix == extension_str:
            return str(path_obj)
        else:
            path_obj = path_obj.with_suffix(extension_str)

        return str(path_obj)


def main():
    app = QApplication(sys.argv)
    # Start LaserComm and connect to laser
    # Use the following call for remote testing (without access to the laser), note that the laser.yaml file must be in
    # the working directory
    # laser = VisaLaser('ASRL3::INSTR', 'laser.yaml@sim')
    laser = CompexLaser('ASRL/dev/ttyAMA1::INSTR', '@py')
    arduino = LaserBrainArduino('/dev/ttyACM0')
    brain = RPiHardware(laser=laser, arduino=arduino)
    ex = PLDMainWindow(laser, brain)
    ex.show()

    sys.exit(app.exec_())


# =============================================================================
# Start the GUI (set up for testing for now)
# FIXME: Need to finalize main loop for proper operation
# =============================================================================
if __name__ == '__main__':
    main()
