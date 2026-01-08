#Project Title - NAMD-Automator: A stand-alone tool for Automating Configuration files for NAMD Simulations.
#Author - Mr. Manojit Mazumder
#Dated - 13.05.2025

import os
import time
import sys
import subprocess
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QSettings
from PyQt5.QtWidgets import (QTextEdit, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QStackedWidget,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QCheckBox, QMessageBox, QComboBox, QDoubleSpinBox,
                             QSpinBox, QRadioButton, QScrollArea, QMainWindow, QTabWidget, QDialogButtonBox, QDialog, QFileDialog, QApplication, QTextBrowser)
from PyQt5.QtGui import QIcon, QPixmap  



def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    # Use the script directory for development
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

 

class Worker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, task_function, *args, **kwargs):
        super().__init__()
        self.task_function = task_function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            if self.task_function():
                self.task_function(*self.args, **self.kwargs)
            else:
                for i in range(100):
                    time.sleep(0.1)
                    self.progress.emit()
                    
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))




       
class MinimizationGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_param_files = []
        self.directory_setup_tab = None  
        # References to other forms (to be set by MainWindow)
        self.heating_form = None
        self.equilibrium_form = None
        self.production_form = None

    def initUI(self):
        
        
        self.min_psf_label = QLabel('PSF File', self)
        self.min_psf_input = QLineEdit(self)
        self.min_psf_button = QPushButton('Browse', self)
        self.min_psf_button.clicked.connect(self.browsePsfFile)

        self.min_pdb_label = QLabel('PDB File', self)
        self.min_pdb_input = QLineEdit(self)
        self.min_pdb_button = QPushButton('Browse', self)
        self.min_pdb_button.clicked.connect(self.browsePdbFile)

        self.min_param_checkbox = QCheckBox('Paratype-CHARMM', self)
        self.min_param_checkbox.stateChanged.connect(self.toggleParamFiles)

        self.min_param_files_label = QLabel('Parameter Files', self)
        self.min_param_files_input = QLineEdit(self)
        self.min_param_files_button = QPushButton('Browse', self)
        self.min_param_files_button.clicked.connect(self.browseParamFiles)

        self.min_exclude_label = QLabel('Exclude scale', self)
        self.min_exclude_combo = QComboBox(self)
        self.min_exclude_combo.addItems(['none', 'scaled1-4'])

        self.min_scaling_label = QLabel('1-4 Scaling', self)
        self.min_scaling_input = QDoubleSpinBox(self)
        self.min_scaling_input.setRange(0, 1.0)
        self.min_scaling_input.setValue(1.0)

        self.min_dielectric_label = QLabel('Dielectric', self)
        self.min_dielectric_input = QDoubleSpinBox(self)
        self.min_dielectric_input.setRange(0, 2.0)
        self.min_dielectric_input.setValue(1.0)

        self.min_switch_checkbox = QCheckBox('Enable Switching', self)
        self.min_switch_checkbox.stateChanged.connect(self.toggleSwitchDistance)

        self.min_switch_distance_label = QLabel('Switch Distance', self)
        self.min_switch_distance_input = QDoubleSpinBox(self)
        self.min_switch_distance_input.setRange(0.0, 12.0)
        self.min_switch_distance_input.setDecimals(1)
        self.min_switch_distance_input.setValue(8.0)
        self.min_switch_distance_input.setEnabled(False)

        self.min_cutoff_label = QLabel('Cut-off', self)
        self.min_cutoff_input = QDoubleSpinBox(self)
        self.min_cutoff_input.setRange(0.0, 30.0)
        self.min_cutoff_input.setValue(12.0)

        self.min_pairlist_distance_label = QLabel('Pairlist Distance', self)
        self.min_pairlist_distance_input = QDoubleSpinBox(self)
        self.min_pairlist_distance_input.setDecimals(2)
        self.min_pairlist_distance_input.setValue(13.5)
        self.min_pairlist_distance_input.setRange(0.0, 100.0)

        self.min_margin_label = QLabel('Margin', self)
        self.min_margin_input = QDoubleSpinBox(self)
        self.min_margin_input.setDecimals(2)
        self.min_margin_input.setValue(2.5)
        self.min_margin_input.setRange(0.0, 10.0)

        self.min_stepspercycle_label = QLabel('Steps per cycle', self)
        self.min_stepspercycle_input = QSpinBox(self)
        self.min_stepspercycle_input.setRange(0, 50)
        self.min_stepspercycle_input.setValue(20)

        self.min_rigidbonds_label = QLabel('Rigid bonds', self)
        self.min_rigidbonds_combo = QComboBox(self)
        self.min_rigidbonds_combo.addItems(['all', 'none'])
        self.min_rigidbonds_combo.setCurrentIndex(0)

        self.min_rigid_tolerance_label = QLabel('Rigid Tolerance', self)
        self.min_rigid_tolerance_input = QDoubleSpinBox(self)
        self.min_rigid_tolerance_input.setDecimals(5)
        self.min_rigid_tolerance_input.setValue(0.00001)
        self.min_rigid_tolerance_input.setRange(0.0, 1.0)

        self.min_rigid_iterations_label = QLabel('Rigid Iterations', self)
        self.min_rigid_iterations_input = QSpinBox(self)
        self.min_rigid_iterations_input.setRange(0, 1000)
        self.min_rigid_iterations_input.setValue(100)

        self.min_pme_label = QLabel('PME', self)
        self.min_pme_on_radio = QRadioButton('On', self)
        self.min_pme_off_radio = QRadioButton('Off', self)
        self.min_pme_off_radio.setChecked(False)

        self.min_pme_tolerance_label = QLabel('PME Tolerance', self)
        self.min_pme_tolerance_input = QDoubleSpinBox(self)
        self.min_pme_tolerance_input.setDecimals(6)
        self.min_pme_tolerance_input.setValue(0.000001)
        self.min_pme_tolerance_input.setRange(0.0, 1.0)

        self.min_pme_grid_x_label = QLabel('PME Grid Size X', self)
        self.min_pme_grid_x_input = QSpinBox(self)
        self.min_pme_grid_x_input.setRange(1, 512)

        self.min_pme_grid_y_label = QLabel('PME Grid Size Y', self)
        self.min_pme_grid_y_input = QSpinBox(self)
        self.min_pme_grid_y_input.setRange(1, 512)

        self.min_pme_grid_z_label = QLabel('PME Grid Size Z', self)
        self.min_pme_grid_z_input = QSpinBox(self)
        self.min_pme_grid_z_input.setRange(1, 512)
        
        self.min_output_energies_label = QLabel('Output Energies', self)
        self.min_output_energies_input = QSpinBox(self)
        self.min_output_energies_input.setRange(0, 10000)
        self.min_output_energies_input.setValue(100)

        self.min_output_timing_label = QLabel('Output Timing', self)
        self.min_output_timing_input = QSpinBox(self)
        self.min_output_timing_input.setRange(0, 10000)
        self.min_output_timing_input.setValue(100)

        self.min_binary_output_label = QLabel('Binary Output', self)
        self.min_binary_output_combo = QComboBox(self)
        self.min_binary_output_combo.addItems(['yes', 'no'])
        self.min_binary_output_combo.setCurrentIndex(1)

        self.min_output_name_label = QLabel('Output Name', self)
        self.min_output_name_input = QLineEdit(self)
        self.min_output_name_input.setText("Complex_min")

        self.min_restart_name_label = QLabel('Restart Name', self)
        self.min_restart_name_input = QLineEdit(self)
        self.min_restart_name_input.setText("Compex_min_restart")

        self.min_restart_freq_label = QLabel('Restart Frequency', self)
        self.min_restart_freq_input = QSpinBox(self)
        self.min_restart_freq_input.setRange(0, 1000000)
        self.min_restart_freq_input.setValue(1000)

        self.min_binary_restart_label = QLabel('Binary Restart', self)
        self.min_binary_restart_combo = QComboBox(self)
        self.min_binary_restart_combo.addItems(['yes', 'no'])
        self.min_binary_restart_combo.setCurrentIndex(1)

        self.min_dcd_file_label = QLabel('DCD File', self)
        self.min_dcd_file_input = QLineEdit(self)
        self.min_dcd_file_input.setText("Complex_min.dcd")

        self.min_dcd_freq_label = QLabel('DCD Frequency', self)
        self.min_dcd_freq_input = QSpinBox(self)
        self.min_dcd_freq_input.setRange(0, 100000000)
        self.min_dcd_freq_input.setValue(1000)

        self.min_num_steps_label = QLabel('Number of Steps', self)
        self.min_num_steps_input = QSpinBox(self)
        self.min_num_steps_input.setRange(0, 100000000)
        self.min_num_steps_input.setValue(6000)

        self.min_cell_basis_vector_label = QLabel("Cell Basis Vectors", self)

        self.min_vector_tabs = QTabWidget()
        self.min_vector1_tab = QWidget()
        self.min_vector2_tab = QWidget()
        self.min_vector3_tab = QWidget()

        self.min_vector1_x_input = QDoubleSpinBox(self)
        self.min_vector1_x_input.setDecimals(3)
        self.min_vector1_x_input.setRange(-999.999, 999.999)
        self.min_vector1_y_input = QDoubleSpinBox(self)
        self.min_vector1_y_input.setDecimals(3)
        self.min_vector1_y_input.setRange(-999.999, 999.999)
        self.min_vector1_z_input = QDoubleSpinBox(self)
        self.min_vector1_z_input.setDecimals(3)
        self.min_vector1_z_input.setRange(-999.999, 999.999)

        vector1_layout = QHBoxLayout()
        vector1_layout.addWidget(QLabel("X:"))
        vector1_layout.addWidget(self.min_vector1_x_input)
        vector1_layout.addWidget(QLabel("Y:"))
        vector1_layout.addWidget(self.min_vector1_y_input)
        vector1_layout.addWidget(QLabel("Z:"))
        vector1_layout.addWidget(self.min_vector1_z_input)
        self.min_vector1_tab.setLayout(vector1_layout)

        self.min_vector2_x_input = QDoubleSpinBox(self)
        self.min_vector2_x_input.setDecimals(3)
        self.min_vector2_x_input.setRange(-999.999, 999.999)
        self.min_vector2_y_input = QDoubleSpinBox(self)
        self.min_vector2_y_input.setDecimals(3)
        self.min_vector2_y_input.setRange(-999.999, 999.999)
        self.min_vector2_z_input = QDoubleSpinBox(self)
        self.min_vector2_z_input.setDecimals(3)
        self.min_vector2_z_input.setRange(-999.999, 999.999)

        vector2_layout = QHBoxLayout()
        vector2_layout.addWidget(QLabel("X:"))
        vector2_layout.addWidget(self.min_vector2_x_input)
        vector2_layout.addWidget(QLabel("Y:"))
        vector2_layout.addWidget(self.min_vector2_y_input)
        vector2_layout.addWidget(QLabel("Z:"))
        vector2_layout.addWidget(self.min_vector2_z_input)
        self.min_vector2_tab.setLayout(vector2_layout)

        self.min_vector3_x_input = QDoubleSpinBox(self)
        self.min_vector3_x_input.setDecimals(3)
        self.min_vector3_x_input.setRange(-999.999, 999.999)
        self.min_vector3_y_input = QDoubleSpinBox(self)
        self.min_vector3_y_input.setDecimals(3)
        self.min_vector3_y_input.setRange(-999.999, 999.999)
        self.min_vector3_z_input = QDoubleSpinBox(self)
        self.min_vector3_z_input.setDecimals(3)
        self.min_vector3_z_input.setRange(-999.999, 999.999)

        vector3_layout = QHBoxLayout()
        vector3_layout.addWidget(QLabel("X:"))
        vector3_layout.addWidget(self.min_vector3_x_input)
        vector3_layout.addWidget(QLabel("Y:"))
        vector3_layout.addWidget(self.min_vector3_y_input)
        vector3_layout.addWidget(QLabel("Z:"))
        vector3_layout.addWidget(self.min_vector3_z_input)
        self.min_vector3_tab.setLayout(vector3_layout)

        self.min_vector_tabs.addTab(self.min_vector1_tab, "Cell Basis Vector 1")
        self.min_vector_tabs.addTab(self.min_vector2_tab, "Cell Basis Vector 2")
        self.min_vector_tabs.addTab(self.min_vector3_tab, "Cell Basis Vector 3")

        self.min_cell_origin_label = QLabel("Cell Origin", self)

        self.min_cell_origin_x_input = QDoubleSpinBox(self)
        self.min_cell_origin_x_input.setDecimals(18)
        self.min_cell_origin_x_input.setRange(-999.999999999999999999, 1000.00000000000000000)

        self.min_cell_origin_y_input = QDoubleSpinBox(self)
        self.min_cell_origin_y_input.setDecimals(18)
        self.min_cell_origin_y_input.setRange(-999.999999999999999999, 1000.00000000000000000)

        self.min_cell_origin_z_input = QDoubleSpinBox(self)
        self.min_cell_origin_z_input.setDecimals(18)
        self.min_cell_origin_z_input.setRange(-999.999999999999999999, 1000.00000000000000000)

        self.min_wrapping_water_combo = QComboBox(self)
        self.min_wrapping_water_label = QLabel('Wrapping Water', self)
        self.min_wrapping_water_combo.addItems(['on', 'off'])
        self.min_wrapping_water_combo.setCurrentIndex(0)

        self.minimize_button = QPushButton('Create Minimization Configuration file', self)
        self.minimize_button.clicked.connect(self.minimizeAction)

        self.extra_label = QLabel("User defined simulation parameters", self)
        self.extra_input = QTextEdit(self)
        self.extra_input.setPlaceholderText("Enter parameters here if necessary...")

        

        psf_layout = QHBoxLayout()
        psf_layout.addWidget(self.min_psf_label)
        psf_layout.addWidget(self.min_psf_input)
        psf_layout.addWidget(self.min_psf_button)

        pdb_layout = QHBoxLayout()
        pdb_layout.addWidget(self.min_pdb_label)
        pdb_layout.addWidget(self.min_pdb_input)
        pdb_layout.addWidget(self.min_pdb_button)

        param_layout = QHBoxLayout()
        param_layout.addWidget(self.min_param_checkbox)

        param_files_layout = QHBoxLayout()
        param_files_layout.addWidget(self.min_param_files_label)
        param_files_layout.addWidget(self.min_param_files_input)
        param_files_layout.addWidget(self.min_param_files_button)

        exclude_layout = QHBoxLayout()
        exclude_layout.addWidget(self.min_exclude_label)
        exclude_layout.addWidget(self.min_exclude_combo)

        scaling_layout = QHBoxLayout()
        scaling_layout.addWidget(self.min_scaling_label)
        scaling_layout.addWidget(self.min_scaling_input)

        dielectric_layout = QHBoxLayout()
        dielectric_layout.addWidget(self.min_dielectric_label)
        dielectric_layout.addWidget(self.min_dielectric_input)

        switch_layout = QHBoxLayout()
        switch_layout.addWidget(self.min_switch_checkbox)
        switch_layout.addWidget(self.min_switch_distance_label)
        switch_layout.addWidget(self.min_switch_distance_input)

        cutoff_layout = QHBoxLayout()
        cutoff_layout.addWidget(self.min_cutoff_label)
        cutoff_layout.addWidget(self.min_cutoff_input)

        pairlist_layout = QHBoxLayout()
        pairlist_layout.addWidget(self.min_pairlist_distance_label)
        pairlist_layout.addWidget(self.min_pairlist_distance_input)

        margin_layout = QHBoxLayout()
        margin_layout.addWidget(self.min_margin_label)
        margin_layout.addWidget(self.min_margin_input)

        stepspercycle_layout = QHBoxLayout()
        stepspercycle_layout.addWidget(self.min_stepspercycle_label)
        stepspercycle_layout.addWidget(self.min_stepspercycle_input)

        rigidbonds_layout = QHBoxLayout()
        rigidbonds_layout.addWidget(self.min_rigidbonds_label)
        rigidbonds_layout.addWidget(self.min_rigidbonds_combo)

        rigid_tolerance_layout = QHBoxLayout()
        rigid_tolerance_layout.addWidget(self.min_rigid_tolerance_label)
        rigid_tolerance_layout.addWidget(self.min_rigid_tolerance_input)

        rigid_iterations_layout = QHBoxLayout()
        rigid_iterations_layout.addWidget(self.min_rigid_iterations_label)
        rigid_iterations_layout.addWidget(self.min_rigid_iterations_input)

        pme_layout = QVBoxLayout()
        pme_radio_layout = QHBoxLayout()
        pme_radio_layout.addWidget(self.min_pme_on_radio)
        pme_radio_layout.addWidget(self.min_pme_off_radio)
        pme_layout.addWidget(self.min_pme_label)
        pme_layout.addLayout(pme_radio_layout)

        pme_tolerance_layout = QHBoxLayout()
        pme_tolerance_layout.addWidget(self.min_pme_tolerance_label)
        pme_tolerance_layout.addWidget(self.min_pme_tolerance_input)

        pme_grid_layout = QVBoxLayout()

        pme_grid_x_layout = QHBoxLayout()
        pme_grid_x_layout.addWidget(self.min_pme_grid_x_label)
        pme_grid_x_layout.addWidget(self.min_pme_grid_x_input)
        pme_grid_layout.addLayout(pme_grid_x_layout)

        pme_grid_y_layout = QHBoxLayout()
        pme_grid_y_layout.addWidget(self.min_pme_grid_y_label)
        pme_grid_y_layout.addWidget(self.min_pme_grid_y_input)
        pme_grid_layout.addLayout(pme_grid_y_layout)

        pme_grid_z_layout = QHBoxLayout()
        pme_grid_z_layout.addWidget(self.min_pme_grid_z_label)
        pme_grid_z_layout.addWidget(self.min_pme_grid_z_input)
        pme_grid_layout.addLayout(pme_grid_z_layout)

        output_energies_layout = QHBoxLayout()
        output_energies_layout.addWidget(self.min_output_energies_label)
        output_energies_layout.addWidget(self.min_output_energies_input)

        output_timing_layout = QHBoxLayout()
        output_timing_layout.addWidget(self.min_output_timing_label)
        output_timing_layout.addWidget(self.min_output_timing_input)

        binary_output_layout = QHBoxLayout()
        binary_output_layout.addWidget(self.min_binary_output_label)
        binary_output_layout.addWidget(self.min_binary_output_combo)

        output_name_layout = QHBoxLayout()
        output_name_layout.addWidget(self.min_output_name_label)
        output_name_layout.addWidget(self.min_output_name_input)

        restart_name_layout = QHBoxLayout()
        restart_name_layout.addWidget(self.min_restart_name_label)
        restart_name_layout.addWidget(self.min_restart_name_input)

        restart_freq_layout = QHBoxLayout()
        restart_freq_layout.addWidget(self.min_restart_freq_label)
        restart_freq_layout.addWidget(self.min_restart_freq_input)

        binary_restart_layout = QHBoxLayout()
        binary_restart_layout.addWidget(self.min_binary_restart_label)
        binary_restart_layout.addWidget(self.min_binary_restart_combo)

        dcd_file_layout = QHBoxLayout()
        dcd_file_layout.addWidget(self.min_dcd_file_label)
        dcd_file_layout.addWidget(self.min_dcd_file_input)

        dcd_freq_layout = QHBoxLayout()
        dcd_freq_layout.addWidget(self.min_dcd_freq_label)
        dcd_freq_layout.addWidget(self.min_dcd_freq_input)

        num_steps_layout = QHBoxLayout()
        num_steps_layout.addWidget(self.min_num_steps_label)
        num_steps_layout.addWidget(self.min_num_steps_input)

        cell_basis_layout = QVBoxLayout()
        cell_basis_layout.addWidget(self.min_cell_basis_vector_label)
        cell_basis_layout.addWidget(self.min_vector_tabs)

        cell_origin_layout = QHBoxLayout()
        cell_origin_layout.addWidget(self.min_cell_origin_label)
        cell_origin_layout.addWidget(self.min_cell_origin_x_input)
        cell_origin_layout.addWidget(self.min_cell_origin_y_input)
        cell_origin_layout.addWidget(self.min_cell_origin_z_input)

        wrapping_water_layout = QHBoxLayout()
        wrapping_water_layout.addWidget(self.min_wrapping_water_label)
        wrapping_water_layout.addWidget(self.min_wrapping_water_combo)
        
        extra_label_layout = QHBoxLayout()
        extra_label_layout.addWidget(self.extra_label)
        extra_label_layout.addWidget(self.extra_input)

        

        main_layout = QVBoxLayout()
        main_layout.addLayout(psf_layout)
        main_layout.addLayout(pdb_layout)
        main_layout.addLayout(param_layout)
        main_layout.addLayout(param_files_layout)
        main_layout.addLayout(exclude_layout)
        main_layout.addLayout(scaling_layout)
        main_layout.addLayout(dielectric_layout)
        main_layout.addLayout(switch_layout)
        main_layout.addLayout(cutoff_layout)
        main_layout.addLayout(pairlist_layout)
        main_layout.addLayout(margin_layout)
        main_layout.addLayout(stepspercycle_layout)
        main_layout.addLayout(rigidbonds_layout)
        main_layout.addLayout(rigid_tolerance_layout)
        main_layout.addLayout(rigid_iterations_layout)
        main_layout.addLayout(pme_layout)
        main_layout.addLayout(pme_tolerance_layout)
        main_layout.addLayout(pme_grid_layout)
        main_layout.addLayout(output_energies_layout)
        main_layout.addLayout(output_timing_layout)
        main_layout.addLayout(binary_output_layout)
        main_layout.addLayout(output_name_layout)
        main_layout.addLayout(restart_name_layout)
        main_layout.addLayout(restart_freq_layout)
        main_layout.addLayout(binary_restart_layout)
        main_layout.addLayout(dcd_file_layout)
        main_layout.addLayout(dcd_freq_layout)
        main_layout.addLayout(num_steps_layout)
        main_layout.addLayout(cell_basis_layout)
        main_layout.addLayout(cell_origin_layout)
        main_layout.addLayout(wrapping_water_layout)
        main_layout.addLayout(extra_label_layout)
        main_layout.addWidget(self.minimize_button)

        self.setLayout(main_layout)





        self.min_param_files_label.setEnabled(False)
        self.min_param_files_input.setEnabled(False)
        self.min_param_files_button.setEnabled(False)

        

    def browsePsfFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open PSF File', '', 'PSF Files (*.psf)')
        if file_name:
            self.min_psf_input.setText(file_name)
            psf_filename = os.path.basename(file_name)
            # Update in other forms if they exist
            if hasattr(self, 'heating_form') and self.heating_form:
                self.heating_form.heat_psf_input.setText(psf_filename)
            if hasattr(self, 'equilibrium_form') and self.equilibrium_form:
                self.equilibrium_form.equil_psf_input.setText(psf_filename)
            if hasattr(self, 'production_form') and self.production_form:
                self.production_form.psf_input.setText(psf_filename)

        
    def browsePdbFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open PDB File', '', 'PDB Files (*.pdb)')
        if file_name:
            self.min_pdb_input.setText(file_name)

    def toggleParamFiles(self):
        is_checked = self.min_param_checkbox.isChecked()
        self.min_param_files_label.setEnabled(is_checked)
        self.min_param_files_input.setEnabled(is_checked)
        self.min_param_files_button.setEnabled(is_checked)
        # Also update in other forms
        if hasattr(self, 'heating_form') and self.heating_form:
            self.heating_form.heat_param_checkbox.setChecked(is_checked)
            self.heating_form.heat_param_files_label.setEnabled(is_checked)
            self.heating_form.heat_param_files_input.setEnabled(is_checked)
            self.heating_form.heat_param_files_button.setEnabled(is_checked)
        if hasattr(self, 'equilibrium_form') and self.equilibrium_form:
            self.equilibrium_form.equil_param_checkbox.setChecked(is_checked)
            self.equilibrium_form.equil_param_files_label.setEnabled(is_checked)
            self.equilibrium_form.equil_param_files_input.setEnabled(is_checked)
            self.equilibrium_form.equil_param_files_button.setEnabled(is_checked)
        if hasattr(self, 'production_form') and self.production_form:
            self.production_form.param_checkbox.setChecked(is_checked)
            self.production_form.param_files_label.setEnabled(is_checked)
            self.production_form.param_files_input.setEnabled(is_checked)
            self.production_form.param_files_button.setEnabled(is_checked)

    def browseParamFiles(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, 'Open Parameter Files', '', 'All Files (*)')
        if file_names:
            self.selected_param_files = file_names
            self.min_param_files_input.setText('\n '.join(file_names))
            param_file_basenames = [os.path.basename(f) for f in file_names]
            param_file_text = '\n '.join(param_file_basenames)
            # Update in other forms if they exist
            if hasattr(self, 'heating_form') and self.heating_form:
                self.heating_form.selected_param_files = file_names
                self.heating_form.heat_param_files_input.setText(param_file_text)
            if hasattr(self, 'equilibrium_form') and self.equilibrium_form:
                self.equilibrium_form.selected_param_files = file_names
                self.equilibrium_form.equil_param_files_input.setText(param_file_text)
            if hasattr(self, 'production_form') and self.production_form:
                self.production_form.selected_param_files = file_names
                self.production_form.param_files_input.setText(param_file_text)

    def toggleSwitchDistance(self):
        is_checked = self.min_switch_checkbox.isChecked()
        self.min_switch_distance_input.setEnabled(is_checked)





    def submitForm(self):
        psf_file = self.min_psf_input.text()
        pdb_file = self.min_pdb_input.text()
        param_files = self.min_param_files_input.text()
        exclude_scaled = self.min_exclude_combo.currentText()
        scaling_value = self.min_scaling_input.value()
        dielectric_constant = self.min_dielectric_input.value()
        pairlist_distance = self.min_pairlist_distance_input.value()
        cutoff = self.min_cutoff_input.value()
        margin = self.min_margin_input.value()
        stepspercycle = self.min_stepspercycle_input.value()
        rigid_bonds = self.min_rigidbonds_combo.currentText()
        rigid_tolerance = self.min_rigid_tolerance_input.value()
        rigid_iterations = self.min_rigid_iterations_input.value()
        pme_enabled = self.min_pme_on_radio.isChecked()
        pme_tolerance = self.min_pme_tolerance_input.value()
        pme_grid_x = self.min_pme_grid_x_input.value()
        pme_grid_y = self.min_pme_grid_y_input.value()
        pme_grid_z = self.min_pme_grid_z_input.value()
        output_energies = self.min_output_energies_input.value()
        output_timing = self.min_output_timing_input.value()
        binary_output = self.min_binary_output_combo.currentText()
        output_name = self.min_output_name_input.text()
        restart_name = self.min_restart_name_input.text()
        restart_freq = self.min_restart_freq_input.value()
        binary_restart = self.min_binary_restart_combo.currentText()
        dcd_file = self.min_dcd_file_input.text()
        dcd_freq = self.min_dcd_freq_input.value()
        num_steps = self.min_num_steps_input.value()
        vector1_1 = self.min_vector1_x_input.value()
        vector1_2 = self.min_vector1_y_input.value()
        vector1_3 = self.min_vector1_z_input.value()
        vector2_1 = self.min_vector2_x_input.value()
        vector2_2 = self.min_vector2_y_input.value()
        vector2_3 = self.min_vector2_z_input.value()
        vector3_1 = self.min_vector3_x_input.value()
        vector3_2 = self.min_vector3_y_input.value()
        vector3_3 = self.min_vector3_z_input.value()
        cell_origin_x = self.min_cell_origin_x_input.value()
        cell_origin_y = self.min_cell_origin_y_input.value()
        cell_origin_z = self.min_cell_origin_z_input.value()
        wrapping_water = self.min_wrapping_water_combo.currentText()
        extra_text = self.extra_input.toPlainText()

        if not psf_file or not pdb_file:
            QMessageBox.warning(self, 'Error', 'Please upload both PSF and PDB files.')
            return False

        if self.min_param_checkbox.isChecked() and not param_files:
            QMessageBox.warning(self, 'Error', 'Please upload parameter files or disable paratypecharm.')
            return False

        if self.min_switch_checkbox.isChecked():
            switch_distance = self.min_switch_distance_input.value()
        else:
            switch_distance = None

        result = self.saveToFile(psf_file, pdb_file, param_files, exclude_scaled, scaling_value, dielectric_constant,
                        switch_distance, cutoff, pairlist_distance, margin, stepspercycle, rigid_bonds,
                        rigid_tolerance, rigid_iterations, pme_enabled, pme_tolerance, pme_grid_x, pme_grid_y,
                        pme_grid_z, output_energies, output_timing, binary_output,
                        output_name, restart_name, restart_freq, binary_restart, dcd_file, dcd_freq, num_steps,
                        vector1_1, vector1_2, vector1_3, vector2_1, vector2_2, vector2_3, vector3_1, vector3_2,
                        vector3_3, cell_origin_x, cell_origin_y, cell_origin_z, wrapping_water, extra_text)
        if result:
            print('Your simulation parameters are saved to configuration file.')
            QMessageBox.information(self, 'Success', 'Your simulation parameters are saved to configuration file.')
        return result

    def saveToFile(self, psf_file, pdb_file, param_files, exclude_scaled, scaling_value, dielectric_constant,
                   switch_distance, cutoff, pairlist_distance, margin, stepspercycle, rigid_bonds,
                   rigid_tolerance, rigid_iterations, pme_enabled, pme_tolerance, pme_grid_x, pme_grid_y, pme_grid_z,
                   output_energies, output_timing, binary_output,
                   output_name, restart_name, restart_freq, binary_restart, dcd_file, dcd_freq, num_steps,
                   vector1_1, vector1_2, vector1_3, vector2_1, vector2_2, vector2_3, vector3_1, vector3_2, vector3_3,
                   cell_origin_x, cell_origin_y, cell_origin_z, wrapping_water, extra_text):

        
        default_name = 'minimization.conf'
        if hasattr(self, 'directory_setup_tab') and self.directory_setup_tab:
            save_dir = self.directory_setup_tab.get_directory()
            if save_dir:
                default_path = os.path.join(save_dir, default_name)
            else:
                default_path = default_name
        else:
            default_path = default_name

        file_name_min, selected_filter = QFileDialog.getSaveFileName(
            self, 
            'Save Configuration File',
            default_path,
            'All Files (*);;Config Files/Inp Files (*.conf *.inp)'
        )
        if not file_name_min:
            return False
        
        if '.' not in file_name_min:
            if 'conf' in selected_filter:
                file_name_min += '.conf'
            elif 'inp' in selected_filter:
                file_name_min += '.inp'
            else:
                file_name_min += '.conf'

        with open(file_name_min, 'w') as file:
            file.write("##############################################\n")
            file.write("#### input topology and initial structure ####\n")
            file.write("##############################################\n")
            file.write(f'structure      {os.path.basename(psf_file)}\n')
            file.write(f'coordinates    {os.path.basename(pdb_file)}\n\n')
            
            file.write("##############################################\n")
            file.write("#### force field block #######################\n")
            file.write("##############################################\n\n")
            file.write("paratypecharmm on\n")
            for param_files in self.selected_param_files:
                file.write(f'parameters      {os.path.basename(param_files)}\n')
            file.write(f'exclude           {exclude_scaled}\n\n')

            file.write("##############################################\n")
            file.write("#### non-bonded interactions #################\n")
            file.write("##############################################\n\n")
            file.write(f'1-4scaling    {scaling_value}\n')
            file.write(f'dielectric     {dielectric_constant}\n\n')
            
            file.write("##############################################\n")
            file.write("### dealing with long-range interactions######\n")
            file.write("##############################################\n\n")
            file.write(f'switching            on \n\n\n')

            file.write("##############################################\n")
            file.write("#### local and nonlocal terms  ###############\n")
            file.write("##############################################\n\n")
            file.write(f'switchdist          {switch_distance}\n')
            file.write(f'cutoff               {cutoff}\n')
            file.write(f'pairlistdist        {pairlist_distance}\n')
            file.write(f'margin              {margin}\n')
            file.write(f'stepspercycle       {stepspercycle}\n')
            file.write(f'rigidBonds          {rigid_bonds}\n')
            file.write(f'rigidTolerance      {rigid_tolerance:.5f}\n')
            file.write(f'rigidIterations     {rigid_iterations}\n\n')
            
            file.write("##############################################\n")
            file.write("#### local and nonlocal terms  ###############\n")
            file.write("##############################################\n\n")
            file.write(f'PME               {"on" if pme_enabled else "off"}\n')
            file.write(f'PMETolerance      {pme_tolerance:.6f}\n')
            file.write(f'PMEGridSizeX      {pme_grid_x}\n')
            file.write(f'PMEGridSizeY      {pme_grid_y}\n')
            file.write(f'PMEGridSizeZ      {pme_grid_z}\n')
            file.write(f'minimization        on\n\n')

            file.write("##############################################\n")
            file.write("###### this block specifies the output #######\n")
            file.write("##############################################\n\n")
            file.write(f'outputenergies    {output_energies}\n')
            file.write(f'outputtiming      {output_timing}\n')
            file.write(f'binaryoutput      {binary_output}\n')
            file.write(f'outputname        {output_name}\n')
            file.write(f'restartname       {restart_name}\n')
            file.write(f'restartfreq       {restart_freq}\n')
            file.write(f'binaryrestart     {binary_restart}\n')
            file.write(f'DCDfile           {dcd_file}\n')
            file.write(f'dcdfreq           {dcd_freq}\n')
            file.write(f'numsteps          {num_steps}\n\n\n')
            if extra_text:
                file.write(f'{extra_text}\n')


            file.write("#########################################################\n")
            file.write("# this block defines periodic boundary conditions #######\n")
            file.write("#########################################################\n")
            file.write(f'cellBasisVector1     {vector1_1} {vector1_2} {vector1_3}\n')
            file.write(f'cellBasisVector2     {vector2_1} {vector2_2} {vector2_3}\n')
            file.write(f'cellBasisVector3     {vector3_1} {vector3_2} {vector3_3}\n')
            file.write(f'cellOrigin           {cell_origin_x} {cell_origin_y} {cell_origin_z}\n\n')
            file.write(f'wrapWater            {wrapping_water}\n')
            
        return True

    def minimizeAction(self):
        result = self.submitForm()
        if result:
            print('Minimization file generated successfully.')
            QMessageBox.information(self, 'Minimization', 'Minimization file generated successfully.')





class HeatingGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_param_files = []
        
    def initUI(self):
        

        self.heat_psf_label = QLabel('PSF File', self)
        self.heat_psf_input = QLineEdit(self)

        self.heat_coor_label = QLabel('Coordinate File', self)
        self.heat_coor_input = QLineEdit(self)
        self.heat_coor_input.setText("Complex_min.coor")

        self.heat_param_checkbox = QCheckBox('Paratype-CHARMM', self)
        self.heat_param_checkbox.stateChanged.connect(self.toggleParamFiles)

        self.heat_param_files_label = QLabel('Parameter Files', self)
        self.heat_param_files_input = QLineEdit(self)
        self.heat_param_files_button = QPushButton('Browse', self)
        self.heat_param_files_button.clicked.connect(self.browseParamFiles)

        self.heat_exclude_label = QLabel('Exclude scale', self)
        self.heat_exclude_combo = QComboBox(self)
        self.heat_exclude_combo.addItems(['none', 'scaled1-4'])

        self.heat_scaling_label = QLabel('1-4 Scaling', self)
        self.heat_scaling_input = QDoubleSpinBox(self)
        self.heat_scaling_input.setRange(0, 1.0)

        self.heat_dielectric_label = QLabel('Dielectric', self)
        self.heat_dielectric_input = QDoubleSpinBox(self)
        self.heat_dielectric_input.setRange(0,2.0)

        self.heat_switch_checkbox = QCheckBox('Enable Switching', self)
        self.heat_switch_checkbox.stateChanged.connect(self.toggleSwitchDistance)

        self.heat_switch_distance_label = QLabel('Switch Distance', self)
        self.heat_switch_distance_input = QDoubleSpinBox(self)
        self.heat_switch_distance_input.setRange(0.0, 12.0)
        self.heat_switch_distance_input.setDecimals(1)
        self.heat_switch_distance_input.setEnabled(False)

        self.heat_cutoff_label = QLabel('Cut-off', self)
        self.heat_cutoff_input = QDoubleSpinBox(self)
        self.heat_cutoff_input.setRange(0.0, 30.0)

        self.heat_pairlist_distance_label = QLabel('Pairlist Distance', self)
        self.heat_pairlist_distance_input = QDoubleSpinBox(self)
        self.heat_pairlist_distance_input.setDecimals(2)
        self.heat_pairlist_distance_input.setRange(0.0, 100.0)

        self.heat_margin_label = QLabel('Margin', self)
        self.heat_margin_input = QDoubleSpinBox(self)
        self.heat_margin_input.setDecimals(2)
        self.heat_margin_input.setRange(0.0, 10.0)

        self.heat_stepspercycle_label = QLabel('Steps per cycle', self)
        self.heat_stepspercycle_input = QSpinBox(self)
        self.heat_stepspercycle_input.setRange(0, 50)
        self.heat_stepspercycle_input.setValue(20)

        self.heat_rigidbonds_label = QLabel('Rigid bonds', self)
        self.heat_rigidbonds_combo = QComboBox(self)
        self.heat_rigidbonds_combo.addItems(['all', 'none'])

        self.heat_rigid_tolerance_label = QLabel('Rigid Tolerance', self)
        self.heat_rigid_tolerance_input = QDoubleSpinBox(self)
        self.heat_rigid_tolerance_input.setDecimals(5)
        self.heat_rigid_tolerance_input.setRange(0.0, 1.0)

        self.heat_rigid_iterations_label = QLabel('Rigid Iterations', self)
        self.heat_rigid_iterations_input = QSpinBox(self)
        self.heat_rigid_iterations_input.setRange(0, 100000)
        
        self.heat_pme_label = QLabel('PME', self)
        self.heat_pme_on_radio = QRadioButton('on', self)
        self.heat_pme_off_radio = QRadioButton('off', self)
        self.heat_pme_on_radio.setChecked(True)

        self.heat_pme_tolerance_label = QLabel('PME Tolerance', self)
        self.heat_pme_tolerance_input = QDoubleSpinBox(self)
        self.heat_pme_tolerance_input.setDecimals(6)
        self.heat_pme_tolerance_input.setRange(0.0, 1.0)

        self.heat_pme_grid_x_label = QLabel('PME Grid Size X', self)
        self.heat_pme_grid_x_input = QSpinBox(self)
        self.heat_pme_grid_x_input.setRange(1, 512)
        
        
        self.heat_pme_grid_y_label = QLabel('PME Grid Size Y', self)
        self.heat_pme_grid_y_input = QSpinBox(self)
        self.heat_pme_grid_y_input.setRange(1, 512)
        
        
        self.heat_pme_grid_z_label = QLabel('PME Grid Size Z', self)
        self.heat_pme_grid_z_input = QSpinBox(self)
        self.heat_pme_grid_z_input.setRange(1, 512)
        

        self.heat_timestep_label = QLabel('Time Step', self)
        self.heat_timestep_input = QDoubleSpinBox(self)
        self.heat_timestep_input.setRange(1, 2)
        self.heat_timestep_input.setValue(1)

        self.heat_fullelectfreq_label = QLabel('Full Electrostatics Frequency', self)
        self.heat_fullelectfreq_input = QSpinBox(self)
        self.heat_fullelectfreq_input.setRange(1, 100)
        self.heat_fullelectfreq_input.setValue(4)

        self.heat_output_energies_label = QLabel('Output Energies', self)
        self.heat_output_energies_input = QSpinBox(self)
        self.heat_output_energies_input.setRange(0, 1000000)
        self.heat_output_energies_input.setValue(100)
        

        self.heat_output_timing_label = QLabel('Output Timing', self)
        self.heat_output_timing_input = QSpinBox(self)
        self.heat_output_timing_input.setRange(0, 1000000)
        self.heat_output_timing_input.setValue(100)        

        self.heat_binary_output_label = QLabel('Binary Output', self)
        self.heat_binary_output_combo = QComboBox(self)
        self.heat_binary_output_combo.addItems(['yes', 'no'])
        self.heat_binary_output_combo.setCurrentIndex(1)

        self.heat_output_name_label = QLabel('Output Name', self)
        self.heat_output_name_input = QLineEdit(self)
        self.heat_output_name_input.setText("Complex_heat")

        self.heat_restart_name_label = QLabel('Restart Name', self)
        self.heat_restart_name_input = QLineEdit(self)
        self.heat_restart_name_input.setText("Complex_heat_restart")

        self.heat_restart_freq_label = QLabel('Restart Frequency', self)
        self.heat_restart_freq_input = QSpinBox(self)
        self.heat_restart_freq_input.setRange(0, 1000000)
        self.heat_restart_freq_input.setValue(1000)

        self.heat_binary_restart_label = QLabel('Binary Restart', self)
        self.heat_binary_restart_combo = QComboBox(self)
        self.heat_binary_restart_combo.addItems(['yes', 'no'])
        self.heat_binary_restart_combo.setCurrentIndex(0)

        self.heat_dcd_file_label = QLabel('DCD File', self)
        self.heat_dcd_file_input = QLineEdit(self)
        self.heat_dcd_file_input.setText("Complex_heat.dcd")

        self.heat_dcd_freq_label = QLabel('DCD Frequency', self)
        self.heat_dcd_freq_input = QSpinBox(self)
        self.heat_dcd_freq_input.setRange(0, 10000000)
        self.heat_dcd_freq_input.setValue(1000)
        
        self.heat_seed_label = QLabel('Seed', self)
        self.heat_seed_input = QSpinBox(self)
        self.heat_seed_input.setRange(1, 10000)
        self.heat_seed_input.setValue(1010)

        self.heat_num_steps_label = QLabel('Number of Steps', self)
        self.heat_num_steps_input = QSpinBox(self)
        self.heat_num_steps_input.setRange(0, 1000000)
        self.heat_num_steps_input.setValue(300000)

        self.heat_temp_label = QLabel('Initial Temperature', self)
        self.heat_temp_input = QSpinBox(self)
        self.heat_temp_input.setRange(0, 1000)
        self.heat_temp_input.setValue(0)

        self.heat_reassignfreq_label = QLabel('Reassign Frequency', self)
        self.heat_reassignfreq_input = QSpinBox(self)
        self.heat_reassignfreq_input.setRange(0, 100)
        self.heat_reassignfreq_input.setValue(1)

        self.heat_reassignincr_label = QLabel('Reassign Increament', self)
        self.heat_reassignincr_input = QDoubleSpinBox(self)
        self.heat_reassignincr_input.setDecimals(3)
        self.heat_reassignincr_input.setRange(0.0, 1.0)
        self.heat_reassignincr_input.setValue(0.001)

        self.heat_reassignhold_label = QLabel('Reassign Hold', self)
        self.heat_reassignhold_input = QSpinBox(self)
        self.heat_reassignhold_input.setRange(1, 1000)
        self.heat_reassignhold_input.setValue(300)

        self.heat_cell_basis_vector_label = QLabel("Cell Basis Vectors", self)

        self.heat_vector_tabs = QTabWidget()
        self.heat_vector1_tab = QWidget()
        self.heat_vector2_tab = QWidget()
        self.heat_vector3_tab = QWidget()

        self.heat_vector1_x_input = QDoubleSpinBox(self)
        self.heat_vector1_x_input.setDecimals(3)
        self.heat_vector1_x_input.setRange(-999.999, 999.999)
        self.heat_vector1_y_input = QDoubleSpinBox(self)
        self.heat_vector1_y_input.setDecimals(3)
        self.heat_vector1_y_input.setRange(-999.999, 999.999)
        self.heat_vector1_z_input = QDoubleSpinBox(self)
        self.heat_vector1_z_input.setDecimals(3)
        self.heat_vector1_z_input.setRange(-999.999, 999.999)

        vector1_layout = QHBoxLayout()
        vector1_layout.addWidget(QLabel("X:"))
        vector1_layout.addWidget(self.heat_vector1_x_input)
        vector1_layout.addWidget(QLabel("Y:"))
        vector1_layout.addWidget(self.heat_vector1_y_input)
        vector1_layout.addWidget(QLabel("Z:"))
        vector1_layout.addWidget(self.heat_vector1_z_input)
        self.heat_vector1_tab.setLayout(vector1_layout)

        self.heat_vector2_x_input = QDoubleSpinBox(self)
        self.heat_vector2_x_input.setDecimals(3)
        self.heat_vector2_x_input.setRange(-999.999, 999.999)
        self.heat_vector2_y_input = QDoubleSpinBox(self)
        self.heat_vector2_y_input.setDecimals(3)
        self.heat_vector2_y_input.setRange(-999.999, 999.999)
        self.heat_vector2_z_input = QDoubleSpinBox(self)
        self.heat_vector2_z_input.setDecimals(3)
        self.heat_vector2_z_input.setRange(-999.999, 999.999)

        vector2_layout = QHBoxLayout()
        vector2_layout.addWidget(QLabel("X:"))
        vector2_layout.addWidget(self.heat_vector2_x_input)
        vector2_layout.addWidget(QLabel("Y:"))
        vector2_layout.addWidget(self.heat_vector2_y_input)
        vector2_layout.addWidget(QLabel("Z:"))
        vector2_layout.addWidget(self.heat_vector2_z_input)
        self.heat_vector2_tab.setLayout(vector2_layout)

        self.heat_vector3_x_input = QDoubleSpinBox(self)
        self.heat_vector3_x_input.setDecimals(3)
        self.heat_vector3_x_input.setRange(-999.999, 999.999)
        self.heat_vector3_y_input = QDoubleSpinBox(self)
        self.heat_vector3_y_input.setDecimals(3)
        self.heat_vector3_y_input.setRange(-999.999, 999.999)
        self.heat_vector3_z_input = QDoubleSpinBox(self)
        self.heat_vector3_z_input.setDecimals(3)
        self.heat_vector3_z_input.setRange(-999.999, 999.999)

        vector3_layout = QHBoxLayout()
        vector3_layout.addWidget(QLabel("X:"))
        vector3_layout.addWidget(self.heat_vector3_x_input)
        vector3_layout.addWidget(QLabel("Y:"))
        vector3_layout.addWidget(self.heat_vector3_y_input)
        vector3_layout.addWidget(QLabel("Z:"))
        vector3_layout.addWidget(self.heat_vector3_z_input)
        self.heat_vector3_tab.setLayout(vector3_layout)

        self.heat_vector_tabs.addTab(self.heat_vector1_tab, "Cell Basis Vector 1")
        self.heat_vector_tabs.addTab(self.heat_vector2_tab, "Cell Basis Vector 2")
        self.heat_vector_tabs.addTab(self.heat_vector3_tab, "Cell Basis Vector 3")

        self.heat_cell_origin_label = QLabel("Cell Origin", self)

        self.heat_cell_origin_x_input = QDoubleSpinBox(self)
        self.heat_cell_origin_x_input.setDecimals(18)
        self.heat_cell_origin_x_input.setRange(-999.999999999999999999, 999.999999999999999999)
        

        self.heat_cell_origin_y_input = QDoubleSpinBox(self)
        self.heat_cell_origin_y_input.setDecimals(18)
        self.heat_cell_origin_y_input.setRange(-999.999999999999999999, 999.999999999999999999)
        

        self.heat_cell_origin_z_input = QDoubleSpinBox(self)
        self.heat_cell_origin_z_input.setDecimals(18)
        self.heat_cell_origin_z_input.setRange(-999.999999999999999999, 999.999999999999999999)
        

        self.heat_wrapping_water_combo = QComboBox(self)
        self.heat_wrapping_water_label = QLabel('Wrapping Water', self)
        self.heat_wrapping_water_combo.addItems(['on', 'off'])
        self.heat_wrapping_water_combo.setCurrentIndex(0)

        self.extra_label = QLabel("User defined simulation parameters", self)
        self.extra_input = QTextEdit(self)
        self.extra_input.setPlaceholderText("Enter parameters here if necessary...")

        self.heating_button = QPushButton('Create Heating Configuration file', self)
        self.heating_button.clicked.connect(self.heatingAction)


        psf_layout = QHBoxLayout()
        psf_layout.addWidget(self.heat_psf_label)
        psf_layout.addWidget(self.heat_psf_input)

        coor_layout = QHBoxLayout()
        coor_layout.addWidget(self.heat_coor_label)
        coor_layout.addWidget(self.heat_coor_input)

        param_layout = QHBoxLayout()
        param_layout.addWidget(self.heat_param_checkbox)

        param_files_layout = QHBoxLayout()
        param_files_layout.addWidget(self.heat_param_files_label)
        param_files_layout.addWidget(self.heat_param_files_input)
        param_files_layout.addWidget(self.heat_param_files_button)

        exclude_layout = QHBoxLayout()
        exclude_layout.addWidget(self.heat_exclude_label)
        exclude_layout.addWidget(self.heat_exclude_combo)

        scaling_layout = QHBoxLayout()
        scaling_layout.addWidget(self.heat_scaling_label)
        scaling_layout.addWidget(self.heat_scaling_input)

        dielectric_layout = QHBoxLayout()
        dielectric_layout.addWidget(self.heat_dielectric_label)
        dielectric_layout.addWidget(self.heat_dielectric_input)

        switch_layout = QHBoxLayout()
        switch_layout.addWidget(self.heat_switch_checkbox)
        switch_layout.addWidget(self.heat_switch_distance_label)
        switch_layout.addWidget(self.heat_switch_distance_input)

        cutoff_layout = QHBoxLayout()
        cutoff_layout.addWidget(self.heat_cutoff_label)
        cutoff_layout.addWidget(self.heat_cutoff_input)

        pairlist_layout = QHBoxLayout()
        pairlist_layout.addWidget(self.heat_pairlist_distance_label)
        pairlist_layout.addWidget(self.heat_pairlist_distance_input)

        margin_layout = QHBoxLayout()
        margin_layout.addWidget(self.heat_margin_label)
        margin_layout.addWidget(self.heat_margin_input)

        stepspercycle_layout = QHBoxLayout()
        stepspercycle_layout.addWidget(self.heat_stepspercycle_label)
        stepspercycle_layout.addWidget(self.heat_stepspercycle_input)

        rigidbonds_layout = QHBoxLayout()
        rigidbonds_layout.addWidget(self.heat_rigidbonds_label)
        rigidbonds_layout.addWidget(self.heat_rigidbonds_combo)

        rigid_tolerance_layout = QHBoxLayout()
        rigid_tolerance_layout.addWidget(self.heat_rigid_tolerance_label)
        rigid_tolerance_layout.addWidget(self.heat_rigid_tolerance_input)

        rigid_iterations_layout = QHBoxLayout()
        rigid_iterations_layout.addWidget(self.heat_rigid_iterations_label)
        rigid_iterations_layout.addWidget(self.heat_rigid_iterations_input)

        pme_layout = QVBoxLayout()
        pme_radio_layout = QHBoxLayout()
        pme_radio_layout.addWidget(self.heat_pme_on_radio)
        pme_radio_layout.addWidget(self.heat_pme_off_radio)
        pme_layout.addWidget(self.heat_pme_label)
        pme_layout.addLayout(pme_radio_layout)

        pme_tolerance_layout = QHBoxLayout()
        pme_tolerance_layout.addWidget(self.heat_pme_tolerance_label)
        pme_tolerance_layout.addWidget(self.heat_pme_tolerance_input)

        pme_grid_layout = QVBoxLayout()

        pme_grid_x_layout = QHBoxLayout()
        pme_grid_x_layout.addWidget(self.heat_pme_grid_x_label)
        pme_grid_x_layout.addWidget(self.heat_pme_grid_x_input)
        pme_grid_layout.addLayout(pme_grid_x_layout)

        pme_grid_y_layout = QHBoxLayout()
        pme_grid_y_layout.addWidget(self.heat_pme_grid_y_label)
        pme_grid_y_layout.addWidget(self.heat_pme_grid_y_input)
        pme_grid_layout.addLayout(pme_grid_y_layout)

        pme_grid_z_layout = QHBoxLayout()
        pme_grid_z_layout.addWidget(self.heat_pme_grid_z_label)
        pme_grid_z_layout.addWidget(self.heat_pme_grid_z_input)
        pme_grid_layout.addLayout(pme_grid_z_layout)

        timestep_layout = QHBoxLayout()
        timestep_layout.addWidget(self.heat_timestep_label)
        timestep_layout.addWidget(self.heat_timestep_input)

        fullelectfreq_layout = QHBoxLayout()
        fullelectfreq_layout.addWidget(self.heat_fullelectfreq_label)
        fullelectfreq_layout.addWidget(self.heat_fullelectfreq_input)

        output_energies_layout = QHBoxLayout()
        output_energies_layout.addWidget(self.heat_output_energies_label)
        output_energies_layout.addWidget(self.heat_output_energies_input)

        output_timing_layout = QHBoxLayout()
        output_timing_layout.addWidget(self.heat_output_timing_label)
        output_timing_layout.addWidget(self.heat_output_timing_input)

        binary_output_layout = QHBoxLayout()
        binary_output_layout.addWidget(self.heat_binary_output_label)
        binary_output_layout.addWidget(self.heat_binary_output_combo)

        output_name_layout = QHBoxLayout()
        output_name_layout.addWidget(self.heat_output_name_label)
        output_name_layout.addWidget(self.heat_output_name_input)

        restart_name_layout = QHBoxLayout()
        restart_name_layout.addWidget(self.heat_restart_name_label)
        restart_name_layout.addWidget(self.heat_restart_name_input)

        restart_freq_layout = QHBoxLayout()
        restart_freq_layout.addWidget(self.heat_restart_freq_label)
        restart_freq_layout.addWidget(self.heat_restart_freq_input)

        binary_restart_layout = QHBoxLayout()
        binary_restart_layout.addWidget(self.heat_binary_restart_label)
        binary_restart_layout.addWidget(self.heat_binary_restart_combo)

        dcd_file_layout = QHBoxLayout()
        dcd_file_layout.addWidget(self.heat_dcd_file_label)
        dcd_file_layout.addWidget(self.heat_dcd_file_input)

        dcd_freq_layout = QHBoxLayout()
        dcd_freq_layout.addWidget(self.heat_dcd_freq_label)
        dcd_freq_layout.addWidget(self.heat_dcd_freq_input)

        seed_layout = QHBoxLayout()
        seed_layout.addWidget(self.heat_seed_label)
        seed_layout.addWidget(self.heat_seed_input)

        num_steps_layout = QHBoxLayout()
        num_steps_layout.addWidget(self.heat_num_steps_label)
        num_steps_layout.addWidget(self.heat_num_steps_input)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.heat_temp_label)
        temp_layout.addWidget(self.heat_temp_input)

        reassignfreq_layout = QHBoxLayout()
        reassignfreq_layout.addWidget(self.heat_reassignfreq_label)
        reassignfreq_layout.addWidget(self.heat_reassignfreq_input)

        reassignincr_layout = QHBoxLayout()
        reassignincr_layout.addWidget(self.heat_reassignincr_label)
        reassignincr_layout.addWidget(self.heat_reassignincr_input)

        reassignhold_layout = QHBoxLayout()
        reassignhold_layout.addWidget(self.heat_reassignhold_label)
        reassignhold_layout.addWidget(self.heat_reassignhold_input)

        cell_basis_layout = QVBoxLayout()
        cell_basis_layout.addWidget(self.heat_cell_basis_vector_label)
        cell_basis_layout.addWidget(self.heat_vector_tabs)

        cell_origin_layout = QHBoxLayout()
        cell_origin_layout.addWidget(self.heat_cell_origin_label)
        cell_origin_layout.addWidget(self.heat_cell_origin_x_input)
        cell_origin_layout.addWidget(self.heat_cell_origin_y_input)
        cell_origin_layout.addWidget(self.heat_cell_origin_z_input)

        wrapping_water_layout = QHBoxLayout()
        wrapping_water_layout.addWidget(self.heat_wrapping_water_label)
        wrapping_water_layout.addWidget(self.heat_wrapping_water_combo)

        extra_label_layout = QHBoxLayout()
        extra_label_layout.addWidget(self.extra_label)
        extra_label_layout.addWidget(self.extra_input)


        main_layout = QVBoxLayout()
        main_layout.addLayout(psf_layout)
        main_layout.addLayout(coor_layout)
        main_layout.addLayout(param_layout)
        main_layout.addLayout(param_files_layout)
        main_layout.addLayout(exclude_layout)
        main_layout.addLayout(scaling_layout)
        main_layout.addLayout(dielectric_layout)
        main_layout.addLayout(switch_layout)
        main_layout.addLayout(cutoff_layout)
        main_layout.addLayout(pairlist_layout)
        main_layout.addLayout(margin_layout)
        main_layout.addLayout(stepspercycle_layout)
        main_layout.addLayout(rigidbonds_layout)
        main_layout.addLayout(rigid_tolerance_layout)
        main_layout.addLayout(rigid_iterations_layout)
        main_layout.addLayout(pme_layout)
        main_layout.addLayout(pme_tolerance_layout)
        main_layout.addLayout(pme_grid_layout)
        main_layout.addLayout(timestep_layout)
        main_layout.addLayout(fullelectfreq_layout)
        main_layout.addLayout(output_energies_layout)
        main_layout.addLayout(output_timing_layout)
        main_layout.addLayout(binary_output_layout)
        main_layout.addLayout(output_name_layout)
        main_layout.addLayout(restart_name_layout)
        main_layout.addLayout(restart_freq_layout)
        main_layout.addLayout(binary_restart_layout)
        main_layout.addLayout(dcd_file_layout)
        main_layout.addLayout(dcd_freq_layout)
        main_layout.addLayout(seed_layout)
        main_layout.addLayout(num_steps_layout)
        main_layout.addLayout(temp_layout)
        main_layout.addLayout(reassignfreq_layout)
        main_layout.addLayout(reassignincr_layout)
        main_layout.addLayout(reassignhold_layout)
        main_layout.addLayout(cell_basis_layout)
        main_layout.addLayout(cell_origin_layout)
        main_layout.addLayout(wrapping_water_layout)
        main_layout.addLayout(extra_label_layout)
        main_layout.addWidget(self.heating_button)

        self.setLayout(main_layout)



        self.heat_param_files_label.setEnabled(False)
        self.heat_param_files_input.setEnabled(False)
        self.heat_param_files_button.setEnabled(False)

      


    def toggleParamFiles(self):
        is_checked = self.heat_param_checkbox.isChecked()
        self.heat_param_files_label.setEnabled(is_checked)
        self.heat_param_files_input.setEnabled(is_checked)
        self.heat_param_files_button.setEnabled(is_checked)
        # Also update in other forms
        if hasattr(self, 'minimization_form') and self.minimization_form:
            self.minimization_form.min_param_checkbox.setChecked(is_checked)
            self.minimization_form.min_param_files_label.setEnabled(is_checked)
            self.minimization_form.min_param_files_input.setEnabled(is_checked)
            self.minimization_form.min_param_files_button.setEnabled(is_checked)
        if hasattr(self, 'equilibrium_form') and self.equilibrium_form:
            self.equilibrium_form.equil_param_checkbox.setChecked(is_checked)
            self.equilibrium_form.equil_param_files_label.setEnabled(is_checked)
            self.equilibrium_form.equil_param_files_input.setEnabled(is_checked)
            self.equilibrium_form.equil_param_files_button.setEnabled(is_checked)
        if hasattr(self, 'production_form') and self.production_form:
            self.production_form.param_checkbox.setChecked(is_checked)
            self.production_form.param_files_label.setEnabled(is_checked)
            self.production_form.param_files_input.setEnabled(is_checked)
            self.production_form.param_files_button.setEnabled(is_checked)

    def browseParamFiles(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, 'Open Parameter Files', '', 'All Files (*)')
        if file_names:
            self.selected_param_files = file_names
            self.heat_param_files_input.setText('\n '.join(file_names))

    def toggleSwitchDistance(self):
        is_checked = self.heat_switch_checkbox.isChecked()
        self.heat_switch_distance_input.setEnabled(is_checked)


    def submitForm(self):
        psf_file = self.heat_psf_input.text()
        coor_file = self.heat_coor_input.text()
        param_files = self.heat_param_files_input.text()
        exclude_scaled = self.heat_exclude_combo.currentText()
        scaling_value = self.heat_scaling_input.value()
        dielectric_constant = self.heat_dielectric_input.value()
        cutoff = self.heat_cutoff_input.value()
        pairlist_distance = self.heat_pairlist_distance_input.value()
        margin = self.heat_margin_input.value()
        stepspercycle = self.heat_stepspercycle_input.value()
        rigid_bonds = self.heat_rigidbonds_combo.currentText()
        rigid_tolerance = self.heat_rigid_tolerance_input.value()
        rigid_iterations = self.heat_rigid_iterations_input.value()
        pme_enabled = self.heat_pme_on_radio.isChecked()
        pme_tolerance = self.heat_pme_tolerance_input.value()
        pme_grid_x = self.heat_pme_grid_x_input.value()
        pme_grid_y = self.heat_pme_grid_y_input.value()
        pme_grid_z = self.heat_pme_grid_z_input.value()
        timestep = self.heat_timestep_input.value()
        fullelectfreq = self.heat_fullelectfreq_input.value()
        output_energies = self.heat_output_energies_input.value()
        output_timing = self.heat_output_timing_input.value()
        binary_output = self.heat_binary_output_combo.currentText()
        output_name = self.heat_output_name_input.text()
        restart_name = self.heat_restart_name_input.text()
        restart_freq = self.heat_restart_freq_input.value()
        binary_restart = self.heat_binary_restart_combo.currentText()
        dcd_file = self.heat_dcd_file_input.text()
        dcd_freq = self.heat_dcd_freq_input.value()
        seed = self.heat_seed_input.value()
        num_steps = self.heat_num_steps_input.value()
        temp = self.heat_temp_input.value()
        reassignfreq = self.heat_reassignfreq_input.value()
        reassignincr = self.heat_reassignincr_input.value()
        reassignhold = self.heat_reassignhold_input.value()
        vector1_1 = self.heat_vector1_x_input.value()
        vector1_2 = self.heat_vector1_y_input.value()
        vector1_3 = self.heat_vector1_z_input.value()
        vector2_1 = self.heat_vector2_x_input.value()
        vector2_2 = self.heat_vector2_y_input.value()
        vector2_3 = self.heat_vector2_z_input.value()
        vector3_1 = self.heat_vector3_x_input.value()
        vector3_2 = self.heat_vector3_y_input.value()
        vector3_3 = self.heat_vector3_z_input.value()
        cell_origin_x = self.heat_cell_origin_x_input.value()
        cell_origin_y = self.heat_cell_origin_y_input.value()
        cell_origin_z = self.heat_cell_origin_z_input.value()
        wrapping_water = self.heat_wrapping_water_combo.currentText()
        extra_text = self.extra_input.toPlainText()

        if self.heat_param_checkbox.isChecked() and not param_files:
            QMessageBox.warning(self, 'Error', 'Please upload parameter files or disable paratypecharm.')
            return False

        if self.heat_switch_checkbox.isChecked():
            switch_distance = self.heat_switch_distance_input.value()
        else:
            switch_distance = None

        result = self.saveToFile(psf_file, coor_file, param_files, exclude_scaled, scaling_value, dielectric_constant, switch_distance,cutoff,
                        pairlist_distance, margin, stepspercycle, rigid_bonds,
                        rigid_tolerance, rigid_iterations, pme_enabled, pme_tolerance, pme_grid_x, pme_grid_y, pme_grid_z,
                        output_energies, timestep, fullelectfreq, output_timing, binary_output,
                        output_name, restart_name, restart_freq, binary_restart, dcd_file, dcd_freq, seed, num_steps,
                        temp, reassignfreq, reassignincr, reassignhold, vector1_1, vector1_2, vector1_3, vector2_1,
                        vector2_2, vector2_3, vector3_1, vector3_2, vector3_3, cell_origin_x, cell_origin_y,
                        cell_origin_z, wrapping_water, extra_text)

        if result:
            print('Your simulation parameters are saved to configuration file.')
            QMessageBox.information(self, 'Success', 'Your simulation parameters are saved to configuration file.')
        return result

    def saveToFile(self, psf_file, coor_file, param_files, exclude_scaled, scaling_value, dielectric_constant, switch_distance,cutoff,
                   pairlist_distance, margin, stepspercycle, rigid_bonds,
                   rigid_tolerance, rigid_iterations, pme_enabled, pme_tolerance, pme_grid_x, pme_grid_y, pme_grid_z,
                   output_energies, timestep, fullelectfreq, output_timing, binary_output,
                   output_name, restart_name, restart_freq, binary_restart, dcd_file, dcd_freq, seed, num_steps, temp,
                   reassignfreq, reassignincr, reassignhold, vector1_1, vector1_2, vector1_3, vector2_1, vector2_2,
                   vector2_3, vector3_1, vector3_2, vector3_3, cell_origin_x, cell_origin_y, cell_origin_z, wrapping_water, extra_text):

        
        default_name = 'heating.conf'
        if hasattr(self, 'directory_setup_tab') and self.directory_setup_tab:
            save_dir = self.directory_setup_tab.get_directory()
            if save_dir:
                default_path = os.path.join(save_dir, default_name)
            else:
                default_path = default_name
        else:
            default_path = default_name

        file_name_ht, selected_filter = QFileDialog.getSaveFileName(self, 'Save Configuration File', default_path, 'All Files (*);;Config Files/Inp Files (*.conf *.inp)')
        if not file_name_ht:
            return False
        
        if '.' not in file_name_ht:
            if 'conf' in selected_filter:
                file_name_ht += '.conf'
            elif 'inp' in selected_filter:
                file_name_ht += '.inp'
            else:
                file_name_ht += '.conf'

        with open(file_name_ht, 'w') as file:
            file.write("##############################################\n")
            file.write("#### input topology and initial structure ####\n")
            file.write("##############################################\n")
            file.write(f'structure          {psf_file}\n')
            file.write(f'coordinates        {coor_file}\n\n\n')

            file.write("##############################################\n")
            file.write("#### force field block #######################\n")
            file.write("##############################################\n\n")
            file.write(f'paratypecharmm on\n')
            for param_files in self.selected_param_files:
                file.write(f'parameters         {os.path.basename(param_files)}\n')
            file.write(f'exclude              {exclude_scaled}\n')
            file.write(f'1-4scaling          {scaling_value}\n')
            file.write(f'dielectric           {dielectric_constant}\n\n\n')

            file.write("##############################################\n")
            file.write("### dealing with long-range interactions######\n")
            file.write("##############################################\n\n")
            file.write(f'switching               on \n')
            file.write(f'switchdist            {switch_distance}\n')
            file.write(f'cutoff                {cutoff}\n')
            file.write(f'pairlistdist          {pairlist_distance}\n')
            file.write(f'margin                {margin}\n')
            file.write(f'stepspercycle         {stepspercycle}\n')
            file.write(f'rigidBonds            {rigid_bonds}\n')
            file.write(f'rigidTolerance        {rigid_tolerance:.5f}\n')
            file.write(f'rigidIterations       {rigid_iterations}\n\n\n')
            
            file.write("##############################################\n")
            file.write("### Ewald electrostatics######################\n")
            file.write("##############################################\n\n")
            file.write(f'PME                   {"on" if pme_enabled else "off"}\n')
            file.write(f'PMETolerance          {pme_tolerance:.6f}\n')
            file.write(f'PMEGridSizeX          {pme_grid_x}\n')
            file.write(f'PMEGridSizeY          {pme_grid_y}\n')
            file.write(f'PMEGridSizeZ          {pme_grid_z}\n\n\n')

            file.write("##############################################\n")
            file.write("### parameters for integrator and MTS ########\n")
            file.write("##############################################\n\n")
            file.write(f'timestep                  {timestep}\n')
            file.write(f'fullElectfrequency        {fullelectfreq}\n\n\n')

            file.write("##############################################\n")
            file.write("### the output ###############################\n")
            file.write("##############################################\n\n")
            file.write(f'outputenergies       {output_energies}\n')
            file.write(f'outputtiming         {output_timing}\n')
            file.write(f'binaryoutput         {binary_output}\n')
            file.write(f'outputname           {output_name}\n')
            file.write(f'restartname          {restart_name}\n')
            file.write(f'restartfreq          {restart_freq}\n')
            file.write(f'binaryrestart        {binary_restart}\n')
            file.write(f'DCDfile              {dcd_file}\n')
            file.write(f'dcdfreq              {dcd_freq}\n\n\n')
            if extra_text:
                file.write(f'{extra_text}\n')

            file.write("##############################################\n")
            file.write("### MD protocol block ########\n")
            file.write("##############################################\n\n")
            file.write(f'seed                   {seed}\n')
            file.write(f'numsteps               {num_steps}\n\n\n')
            file.write(f'temperature            {temp}\n')
            file.write(f'reassignFreq           {reassignfreq}\n')
            file.write(f'reassignIncr           {reassignincr}\n')
            file.write(f'reassignHold           {reassignhold}\n\n\n')
            
            file.write("#########################################################\n")
            file.write("# this block defines periodic boundary conditions #######\n")
            file.write("#########################################################\n")
            file.write(f'cellBasisVector1         {vector1_1} {vector1_2} {vector1_3}\n')
            file.write(f'cellBasisVector2         {vector2_1} {vector2_2} {vector2_3}\n')
            file.write(f'cellBasisVector3         {vector3_1} {vector3_2} {vector3_3}\n')
            file.write(f'cellOrigin               {cell_origin_x} {cell_origin_y} {cell_origin_z}\n\n')
            file.write(f'wrapWater                {wrapping_water}\n')
            
        return True

    def heatingAction(self):
        result = self.submitForm()
        if result:
            print('Heating file generated successfully.')
            QMessageBox.information(self, 'Heating', 'Heating file generated successfully.')





class EquilibriumGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_param_files = []

    def initUI(self):


        self.equil_psf_label = QLabel('PSF File', self)
        self.equil_psf_input = QLineEdit(self)

        self.equil_coor_label = QLabel('Coordinate File', self)
        self.equil_coor_input = QLineEdit(self)
        self.equil_coor_input.setText("Complex_heat.coor")

        self.equil_vel_label = QLabel('Velocity File', self)
        self.equil_vel_input =QLineEdit(self)
        self.equil_vel_input.setText("Complex_heat.vel")

        self.equil_extsystem_label = QLabel('Extended System File', self)
        self.equil_extsystem_input = QLineEdit(self)
        self.equil_extsystem_input.setText("Complex_heat.xsc")

        self.equil_param_checkbox = QCheckBox('Paratype-CHARMM', self)
        self.equil_param_checkbox.stateChanged.connect(self.toggleParamFiles)

        self.equil_param_files_label = QLabel('Parameter Files', self)
        self.equil_param_files_input = QLineEdit(self)
        self.equil_param_files_button = QPushButton('Browse', self)
        self.equil_param_files_button.clicked.connect(self.browseParamFiles)

        self.equil_exclude_label = QLabel('Exclude Scaled', self)
        self.equil_exclude_combo = QComboBox(self)
        self.equil_exclude_combo.addItems(['none', 'scaled1-4'])

        self.equil_scaling_label = QLabel('1-4 Scaling', self)
        self.equil_scaling_input = QDoubleSpinBox(self)
        self.equil_scaling_input.setRange(0, 1.0)
        
        self.equil_dielectric_label = QLabel('Dielectric', self)
        self.equil_dielectric_input = QDoubleSpinBox(self)
        self.equil_dielectric_input.setRange(0, 1.0)

        self.equil_switch_checkbox = QCheckBox('Enable Switching', self)
        self.equil_switch_checkbox.stateChanged.connect(self.toggleSwitchDistance)

        self.equil_cutoff_label = QLabel('Cut-off', self)
        self.equil_cutoff_input = QDoubleSpinBox(self)
        self.equil_cutoff_input.setRange(0.0, 30.0)
        
        self.equil_switch_distance_label = QLabel('Switch Distance', self)
        self.equil_switch_distance_input = QDoubleSpinBox(self)
        self.equil_switch_distance_input.setRange(0.0, 12.0)
        self.equil_switch_distance_input.setDecimals(1)
        self.equil_switch_distance_input.setEnabled(False)

        self.equil_pairlist_distance_label = QLabel('Pairlist Distance', self)
        self.equil_pairlist_distance_input = QDoubleSpinBox(self)
        self.equil_pairlist_distance_input.setDecimals(2)
        self.equil_pairlist_distance_input.setRange(0.0, 100.0)

        self.equil_margin_label = QLabel('Margin', self)
        self.equil_margin_input = QDoubleSpinBox(self)
        self.equil_margin_input.setDecimals(2)
        self.equil_margin_input.setRange(0.0, 10.0)

        self.equil_stepspercycle_label = QLabel('Steps per cycle', self)
        self.equil_stepspercycle_input = QSpinBox(self)
        self.equil_stepspercycle_input.setRange(0, 50)

        self.equil_rigidbonds_label = QLabel('Rigid bonds', self)
        self.equil_rigidbonds_combo = QComboBox(self)
        self.equil_rigidbonds_combo.addItems(['all', 'none'])

        self.equil_rigid_tolerance_label = QLabel('Rigid Tolerance', self)
        self.equil_rigid_tolerance_input = QDoubleSpinBox(self)
        self.equil_rigid_tolerance_input.setDecimals(5)
        self.equil_rigid_tolerance_input.setRange(0.0, 1.0)

        self.equil_rigid_iterations_label = QLabel('Rigid Iterations', self)
        self.equil_rigid_iterations_input = QSpinBox(self)
        self.equil_rigid_iterations_input.setRange(0, 1000)

        self.equil_langevindynamics_label = QLabel('Langevin Dynamics', self)
        self.equil_langevindynamics_combo = QComboBox(self)
        self.equil_langevindynamics_combo.addItems(['on', 'off'])
        self.equil_langevindynamics_combo.setCurrentIndex(0)

        self.equil_langevin_damping_label = QLabel('Langevin Damping', self)
        self.equil_langevin_damping_input = QSpinBox(self)
        self.equil_langevin_damping_input.setRange(0,2)
        self.equil_langevin_damping_input.setValue(1)

        self.equil_langevintemp_label = QLabel('Langevin Temperature', self)
        self.equil_langevintemp_input = QSpinBox(self)
        self.equil_langevintemp_input.setRange(0,100000)
        self.equil_langevintemp_input.setValue(300)

        self.equil_langevinhydrogen_label = QLabel('Langevin Hydrogen', self)
        self.equil_langevinhydrogen_combo = QComboBox(self)
        self.equil_langevinhydrogen_combo.addItems(['on', 'off'])
        self.equil_langevinhydrogen_combo.setCurrentIndex(1)

        self.equil_usegroup_pressure_label = QLabel('Use Group Pressure', self)
        self.equil_usegroup_pressure_combo = QComboBox(self)
        self.equil_usegroup_pressure_combo.addItems(['yes', 'no'])
        self.equil_usegroup_pressure_combo.setCurrentIndex(0)

        self.equil_useflexiblecell_label = QLabel('Use Flexible Cell', self)
        self.equil_useflexiblecell_combo = QComboBox(self)
        self.equil_useflexiblecell_combo.addItems(['yes', 'no'])
        self.equil_useflexiblecell_combo.setCurrentIndex(1)

        self.equil_useconstantarea_label = QLabel('Use Constant Area', self)
        self.equil_useconstantarea_combo = QComboBox(self)
        self.equil_useconstantarea_combo.addItems(['yes', 'no'])
        self.equil_useconstantarea_combo.setCurrentIndex(1)

        self.equil_langevinpiston_label = QLabel('Langevin Piston', self)
        self.equil_langevinpiston_combo = QComboBox(self)
        self.equil_langevinpiston_combo.addItems(['off', 'on'])
        self.equil_langevinpiston_combo.setCurrentIndex(1)

        self.equil_langevinpistontarget_label = QLabel('Langevin Piston Target', self)
        self.equil_langevinpistontarget_input = QDoubleSpinBox(self)
        self.equil_langevinpistontarget_input.setDecimals(5)
        self.equil_langevinpistontarget_input.setValue(1.01325)
        self.equil_langevinpistontarget_input.setRange(0.0, 10.0)

        self.equil_langevinpistonperiod_label = QLabel('Langevin Piston Period', self)
        self.equil_langevinpistonperiod_input = QSpinBox(self)
        self.equil_langevinpistonperiod_input.setRange(0, 500)
        self.equil_langevinpistonperiod_input.setValue(100)

        self.equil_langevinpistondecay_label = QLabel('Langevin Piston Decay', self)
        self.equil_langevinpistondecay_input = QDoubleSpinBox(self)
        self.equil_langevinpistondecay_input.setDecimals(2)
        self.equil_langevinpistondecay_input.setValue(50)
        self.equil_langevinpistondecay_input.setRange(0.0, 100.0)

        self.equil_langevinpistontemp_label = QLabel('Langevin Piston Temperature', self)
        self.equil_langevinpistontemp_input = QSpinBox(self)
        self.equil_langevinpistontemp_input.setRange(0,100000)
        self.equil_langevinpistontemp_input.setValue(300)
        
        self.equil_pme_label = QLabel('PME', self)
        self.equil_pme_on_radio = QRadioButton('on', self)
        self.equil_pme_off_radio = QRadioButton('off', self)
        self.equil_pme_on_radio.setChecked(True)

        self.equil_pme_tolerance_label = QLabel('PME Tolerance', self)
        self.equil_pme_tolerance_input = QDoubleSpinBox(self)
        self.equil_pme_tolerance_input.setDecimals(6)
        self.equil_pme_tolerance_input.setRange(0.0, 1.0)

        self.equil_pme_grid_x_label = QLabel('PME Grid Size X', self)
        self.equil_pme_grid_x_input = QSpinBox(self)
        self.equil_pme_grid_x_input.setRange(1, 512)

        self.equil_pme_grid_y_label = QLabel('PME Grid Size Y', self)
        self.equil_pme_grid_y_input = QSpinBox(self)
        self.equil_pme_grid_y_input.setRange(1, 512)

        self.equil_pme_grid_z_label = QLabel('PME Grid Size Z', self)
        self.equil_pme_grid_z_input = QSpinBox(self)
        self.equil_pme_grid_z_input.setRange(1, 512)

        self.equil_timestep_label = QLabel('Time Step', self)
        self.equil_timestep_input = QDoubleSpinBox(self)
        self.equil_timestep_input.setRange(1, 2)
        self.equil_timestep_input.setValue(1)

        self.equil_fullelectfreq_label = QLabel('Full Electrostatics Frequency', self)
        self.equil_fullelectfreq_input = QSpinBox(self)
        self.equil_fullelectfreq_input.setRange(1, 100)
        self.equil_fullelectfreq_input.setValue(4)

        self.equil_output_energies_label = QLabel('Output Energies', self)
        self.equil_output_energies_input = QSpinBox(self)
        self.equil_output_energies_input.setRange(0, 1000000)
        self.equil_output_energies_input.setValue(1000)

        self.equil_output_timing_label = QLabel('Output Timing', self)
        self.equil_output_timing_input = QSpinBox(self)
        self.equil_output_timing_input.setRange(0, 1000000)
        self.equil_output_timing_input.setValue(1000)

        self.equil_binary_output_label = QLabel('Binary Output', self)
        self.equil_binary_output_combo = QComboBox(self)
        self.equil_binary_output_combo.addItems(['yes', 'no'])
        self.equil_binary_output_combo.setCurrentIndex(1)

        self.equil_output_name_label = QLabel('Output Name', self)
        self.equil_output_name_input = QLineEdit(self)
        self.equil_output_name_input.setText("Complex_equil")

        self.equil_restart_name_label = QLabel('Restart Name', self)
        self.equil_restart_name_input = QLineEdit(self)
        self.equil_restart_name_input.setText("Complex_equil_restart")

        self.equil_restart_freq_label = QLabel('Restart Frequency', self)
        self.equil_restart_freq_input = QSpinBox(self)
        self.equil_restart_freq_input.setRange(0, 1000000)
        self.equil_restart_freq_input.setValue(1000)

        self.equil_binary_restart_label = QLabel('Binary Restart', self)
        self.equil_binary_restart_combo = QComboBox(self)
        self.equil_binary_restart_combo.addItems(['yes', 'no'])
        self.equil_binary_restart_combo.setCurrentIndex(0)

        self.equil_dcd_file_label = QLabel('DCD File', self)
        self.equil_dcd_file_input = QLineEdit(self)
        self.equil_dcd_file_input.setText("Complex_equil.dcd")

        self.equil_dcd_freq_label = QLabel('DCD Frequency', self)
        self.equil_dcd_freq_input = QSpinBox(self)
        self.equil_dcd_freq_input.setRange(0, 1000000)
        self.equil_dcd_freq_input.setValue(1000)

        self.equil_seed_label = QLabel('Seed', self)
        self.equil_seed_input = QSpinBox(self)
        self.equil_seed_input.setRange(1, 10000)
        self.equil_seed_input.setValue(2010)

        self.equil_num_steps_label = QLabel('Number of Steps', self)
        self.equil_num_steps_input = QSpinBox(self)
        self.equil_num_steps_input.setRange(0, 100000000)
        self.equil_num_steps_input.setValue(1000000)

        self.equil_rescalefreq_label = QLabel('Rescale Frequency', self)
        self.equil_rescalefreq_input = QSpinBox(self)
        self.equil_rescalefreq_input.setRange(0, 10)
        self.equil_rescalefreq_input.setValue(1)

        self.equil_rescaletemp_label = QLabel('Rescale Temperature', self)
        self.equil_rescaletemp_input = QSpinBox(self)
        self.equil_rescaletemp_input.setRange(1, 1000)
        self.equil_rescaletemp_input.setValue(300)

        self.equil_cell_basis_vector_label = QLabel("Cell Basis Vectors", self)

        self.equil_vector_tabs = QTabWidget()
        self.equil_vector1_tab = QWidget()
        self.equil_vector2_tab = QWidget()
        self.equil_vector3_tab = QWidget()

        self.equil_vector1_x_input = QDoubleSpinBox(self)
        self.equil_vector1_x_input.setDecimals(3)
        self.equil_vector1_x_input.setRange(-999.999, 999.999)
        self.equil_vector1_y_input = QDoubleSpinBox(self)
        self.equil_vector1_y_input.setDecimals(3)
        self.equil_vector1_y_input.setRange(-999.999, 999.999)
        self.equil_vector1_z_input = QDoubleSpinBox(self)
        self.equil_vector1_z_input.setDecimals(3)
        self.equil_vector1_z_input.setRange(-999.999, 999.999)

        vector1_layout = QHBoxLayout()
        vector1_layout.addWidget(QLabel("X:"))
        vector1_layout.addWidget(self.equil_vector1_x_input)
        vector1_layout.addWidget(QLabel("Y:"))
        vector1_layout.addWidget(self.equil_vector1_y_input)
        vector1_layout.addWidget(QLabel("Z:"))
        vector1_layout.addWidget(self.equil_vector1_z_input)
        self.equil_vector1_tab.setLayout(vector1_layout)

        self.equil_vector2_x_input = QDoubleSpinBox(self)
        self.equil_vector2_x_input.setDecimals(3)
        self.equil_vector2_x_input.setRange(-999.999, 999.999)
        self.equil_vector2_y_input = QDoubleSpinBox(self)
        self.equil_vector2_y_input.setDecimals(3)
        self.equil_vector2_y_input.setRange(-999.999, 999.999)
        self.equil_vector2_z_input = QDoubleSpinBox(self)
        self.equil_vector2_z_input.setDecimals(3)
        self.equil_vector2_z_input.setRange(-999.999, 999.999)

        vector2_layout = QHBoxLayout()
        vector2_layout.addWidget(QLabel("X:"))
        vector2_layout.addWidget(self.equil_vector2_x_input)
        vector2_layout.addWidget(QLabel("Y:"))
        vector2_layout.addWidget(self.equil_vector2_y_input)
        vector2_layout.addWidget(QLabel("Z:"))
        vector2_layout.addWidget(self.equil_vector2_z_input)
        self.equil_vector2_tab.setLayout(vector2_layout)

        self.equil_vector3_x_input = QDoubleSpinBox(self)
        self.equil_vector3_x_input.setDecimals(3)
        self.equil_vector3_x_input.setRange(-999.999, 999.999)
        self.equil_vector3_y_input = QDoubleSpinBox(self)
        self.equil_vector3_y_input.setDecimals(3)
        self.equil_vector3_y_input.setRange(-999.999, 999.999)
        self.equil_vector3_z_input = QDoubleSpinBox(self)
        self.equil_vector3_z_input.setDecimals(3)
        self.equil_vector3_z_input.setRange(-999.999, 999.999)

        vector3_layout = QHBoxLayout()
        vector3_layout.addWidget(QLabel("X:"))
        vector3_layout.addWidget(self.equil_vector3_x_input)
        vector3_layout.addWidget(QLabel("Y:"))
        vector3_layout.addWidget(self.equil_vector3_y_input)
        vector3_layout.addWidget(QLabel("Z:"))
        vector3_layout.addWidget(self.equil_vector3_z_input)
        self.equil_vector3_tab.setLayout(vector3_layout)

        self.equil_vector_tabs.addTab(self.equil_vector1_tab, "Cell Basis Vector 1")
        self.equil_vector_tabs.addTab(self.equil_vector2_tab, "Cell Basis Vector 2")
        self.equil_vector_tabs.addTab(self.equil_vector3_tab, "Cell Basis Vector 3")

        self.equil_cell_origin_label = QLabel("Cell Origin", self)

        self.equil_cell_origin_x_input = QDoubleSpinBox(self)
        self.equil_cell_origin_x_input.setDecimals(18)
        self.equil_cell_origin_x_input.setRange(-999.999999999999999999, 999.999999999999999999)
        
        self.equil_cell_origin_y_input = QDoubleSpinBox(self)
        self.equil_cell_origin_y_input.setDecimals(18)
        self.equil_cell_origin_y_input.setRange(-999.999999999999999999, 999.999999999999999999)
        
        self.equil_cell_origin_z_input = QDoubleSpinBox(self)
        self.equil_cell_origin_z_input.setDecimals(18)
        self.equil_cell_origin_z_input.setRange(-999.999999999999999999, 999.999999999999999999)
        
        self.equil_wrapping_water_combo = QComboBox(self)
        self.equil_wrapping_water_label = QLabel('Wrapping Water', self)
        self.equil_wrapping_water_combo.addItems(['on', 'off'])
        self.equil_wrapping_water_combo.setCurrentIndex(0)

        self.extra_label = QLabel("User defined simulation parameters", self)
        self.extra_input = QTextEdit(self)
        self.extra_input.setPlaceholderText("Enter parameters here if necessary...")
        
        self.equilibrium_button = QPushButton('Create Equilibration Configuration file', self)
        self.equilibrium_button.clicked.connect(self.equilibriumAction)



        psf_layout = QHBoxLayout()
        psf_layout.addWidget(self.equil_psf_label)
        psf_layout.addWidget(self.equil_psf_input)

        coor_layout = QHBoxLayout()
        coor_layout.addWidget(self.equil_coor_label)
        coor_layout.addWidget(self.equil_coor_input)

        vel_layout = QHBoxLayout()
        vel_layout.addWidget(self.equil_vel_label)
        vel_layout.addWidget(self.equil_vel_input)

        extsystem_layout = QHBoxLayout()
        extsystem_layout.addWidget(self.equil_extsystem_label)
        extsystem_layout.addWidget(self.equil_extsystem_input)

        param_layout = QHBoxLayout()
        param_layout.addWidget(self.equil_param_checkbox)

        param_files_layout = QHBoxLayout()
        param_files_layout.addWidget(self.equil_param_files_label)
        param_files_layout.addWidget(self.equil_param_files_input)
        param_files_layout.addWidget(self.equil_param_files_button)

        exclude_layout = QHBoxLayout()
        exclude_layout.addWidget(self.equil_exclude_label)
        exclude_layout.addWidget(self.equil_exclude_combo)

        scaling_layout = QHBoxLayout()
        scaling_layout.addWidget(self.equil_scaling_label)
        scaling_layout.addWidget(self.equil_scaling_input)

        dielectric_layout = QHBoxLayout()
        dielectric_layout.addWidget(self.equil_dielectric_label)
        dielectric_layout.addWidget(self.equil_dielectric_input)

        switch_layout = QHBoxLayout()
        switch_layout.addWidget(self.equil_switch_checkbox)
        switch_layout.addWidget(self.equil_switch_distance_label)
        switch_layout.addWidget(self.equil_switch_distance_input)

        cutoff_layout = QHBoxLayout()
        cutoff_layout.addWidget(self.equil_cutoff_label)
        cutoff_layout.addWidget(self.equil_cutoff_input)

        pairlist_layout = QHBoxLayout()
        pairlist_layout.addWidget(self.equil_pairlist_distance_label)
        pairlist_layout.addWidget(self.equil_pairlist_distance_input)

        margin_layout = QHBoxLayout()
        margin_layout.addWidget(self.equil_margin_label)
        margin_layout.addWidget(self.equil_margin_input)

        stepspercycle_layout = QHBoxLayout()
        stepspercycle_layout.addWidget(self.equil_stepspercycle_label)
        stepspercycle_layout.addWidget(self.equil_stepspercycle_input)

        rigidbonds_layout = QHBoxLayout()
        rigidbonds_layout.addWidget(self.equil_rigidbonds_label)
        rigidbonds_layout.addWidget(self.equil_rigidbonds_combo)

        rigid_tolerance_layout = QHBoxLayout()
        rigid_tolerance_layout.addWidget(self.equil_rigid_tolerance_label)
        rigid_tolerance_layout.addWidget(self.equil_rigid_tolerance_input)

        rigid_iterations_layout = QHBoxLayout()
        rigid_iterations_layout.addWidget(self.equil_rigid_iterations_label)
        rigid_iterations_layout.addWidget(self.equil_rigid_iterations_input)

        langevindynamics_layout = QHBoxLayout()
        langevindynamics_layout.addWidget(self.equil_langevindynamics_label)
        langevindynamics_layout.addWidget(self.equil_langevindynamics_combo)

        langevindamping_layout = QHBoxLayout()
        langevindamping_layout.addWidget(self.equil_langevin_damping_label)
        langevindamping_layout.addWidget(self.equil_langevin_damping_input)

        langevintemp_layout = QHBoxLayout()
        langevintemp_layout.addWidget(self.equil_langevintemp_label)
        langevintemp_layout.addWidget(self.equil_langevintemp_input)

        langevinhydrogen_layout = QHBoxLayout()
        langevinhydrogen_layout.addWidget(self.equil_langevinhydrogen_label)
        langevinhydrogen_layout.addWidget(self.equil_langevinhydrogen_combo)

        usegroup_pressure_layout = QHBoxLayout()
        usegroup_pressure_layout.addWidget(self.equil_usegroup_pressure_label)
        usegroup_pressure_layout.addWidget(self.equil_usegroup_pressure_combo)

        useflexiblecell_layout = QHBoxLayout()
        useflexiblecell_layout.addWidget(self.equil_useflexiblecell_label)
        useflexiblecell_layout.addWidget(self.equil_useflexiblecell_combo)

        useconstantarea_layout = QHBoxLayout()
        useconstantarea_layout.addWidget(self.equil_useconstantarea_label)
        useconstantarea_layout.addWidget(self.equil_useconstantarea_combo)

        langevinpiston_layout = QHBoxLayout()
        langevinpiston_layout.addWidget(self.equil_langevinpiston_label)
        langevinpiston_layout.addWidget(self.equil_langevinpiston_combo)

        langevinpistontarget_layout = QHBoxLayout()
        langevinpistontarget_layout.addWidget(self.equil_langevinpistontarget_label)
        langevinpistontarget_layout.addWidget(self.equil_langevinpistontarget_input)

        langevinpistonperiod_layout = QHBoxLayout()
        langevinpistonperiod_layout.addWidget(self.equil_langevinpistonperiod_label)
        langevinpistonperiod_layout.addWidget(self.equil_langevinpistonperiod_input)

        langevinpistondecay_layout = QHBoxLayout()
        langevinpistondecay_layout.addWidget(self.equil_langevinpistondecay_label)
        langevinpistondecay_layout.addWidget(self.equil_langevinpistondecay_input)

        langevinpistontemp_layout = QHBoxLayout()
        langevinpistontemp_layout.addWidget(self.equil_langevinpistontemp_label)
        langevinpistontemp_layout.addWidget(self.equil_langevinpistontemp_input)

        pme_layout = QVBoxLayout()
        pme_radio_layout = QHBoxLayout()
        pme_radio_layout.addWidget(self.equil_pme_on_radio)
        pme_radio_layout.addWidget(self.equil_pme_off_radio)
        pme_layout.addWidget(self.equil_pme_label)
        pme_layout.addLayout(pme_radio_layout)

        pme_tolerance_layout = QHBoxLayout()
        pme_tolerance_layout.addWidget(self.equil_pme_tolerance_label)
        pme_tolerance_layout.addWidget(self.equil_pme_tolerance_input)

        pme_grid_layout = QVBoxLayout()

        pme_grid_x_layout = QHBoxLayout()
        pme_grid_x_layout.addWidget(self.equil_pme_grid_x_label)
        pme_grid_x_layout.addWidget(self.equil_pme_grid_x_input)
        pme_grid_layout.addLayout(pme_grid_x_layout)

        pme_grid_y_layout = QHBoxLayout()
        pme_grid_y_layout.addWidget(self.equil_pme_grid_y_label)
        pme_grid_y_layout.addWidget(self.equil_pme_grid_y_input)
        pme_grid_layout.addLayout(pme_grid_y_layout)

        pme_grid_z_layout = QHBoxLayout()
        pme_grid_z_layout.addWidget(self.equil_pme_grid_z_label)
        pme_grid_z_layout.addWidget(self.equil_pme_grid_z_input)
        pme_grid_layout.addLayout(pme_grid_z_layout)

        timestep_layout = QHBoxLayout()
        timestep_layout.addWidget(self.equil_timestep_label)
        timestep_layout.addWidget(self.equil_timestep_input)

        fullelectfreq_layout = QHBoxLayout()
        fullelectfreq_layout.addWidget(self.equil_fullelectfreq_label)
        fullelectfreq_layout.addWidget(self.equil_fullelectfreq_input)

        output_energies_layout = QHBoxLayout()
        output_energies_layout.addWidget(self.equil_output_energies_label)
        output_energies_layout.addWidget(self.equil_output_energies_input)

        output_timing_layout = QHBoxLayout()
        output_timing_layout.addWidget(self.equil_output_timing_label)
        output_timing_layout.addWidget(self.equil_output_timing_input)

        binary_output_layout = QHBoxLayout()
        binary_output_layout.addWidget(self.equil_binary_output_label)
        binary_output_layout.addWidget(self.equil_binary_output_combo)

        output_name_layout = QHBoxLayout()
        output_name_layout.addWidget(self.equil_output_name_label)
        output_name_layout.addWidget(self.equil_output_name_input)

        restart_name_layout = QHBoxLayout()
        restart_name_layout.addWidget(self.equil_restart_name_label)
        restart_name_layout.addWidget(self.equil_restart_name_input)

        restart_freq_layout = QHBoxLayout()
        restart_freq_layout.addWidget(self.equil_restart_freq_label)
        restart_freq_layout.addWidget(self.equil_restart_freq_input)

        binary_restart_layout = QHBoxLayout()
        binary_restart_layout.addWidget(self.equil_binary_restart_label)
        binary_restart_layout.addWidget(self.equil_binary_restart_combo)

        dcd_file_layout = QHBoxLayout()
        dcd_file_layout.addWidget(self.equil_dcd_file_label)
        dcd_file_layout.addWidget(self.equil_dcd_file_input)
        

        dcd_freq_layout = QHBoxLayout()
        dcd_freq_layout.addWidget(self.equil_dcd_freq_label)
        dcd_freq_layout.addWidget(self.equil_dcd_freq_input)

        seed_layout = QHBoxLayout()
        seed_layout.addWidget(self.equil_seed_label)
        seed_layout.addWidget(self.equil_seed_input)

        num_steps_layout = QHBoxLayout()
        num_steps_layout.addWidget(self.equil_num_steps_label)
        num_steps_layout.addWidget(self.equil_num_steps_input)
        
        rescalefreq_layout = QHBoxLayout()
        rescalefreq_layout.addWidget(self.equil_rescalefreq_label)
        rescalefreq_layout.addWidget(self.equil_rescalefreq_input)

        rescaletemp_layout = QHBoxLayout()
        rescaletemp_layout.addWidget(self.equil_rescaletemp_label)
        rescaletemp_layout.addWidget(self.equil_rescaletemp_input)

        cell_basis_layout = QVBoxLayout()
        cell_basis_layout.addWidget(self.equil_cell_basis_vector_label)
        cell_basis_layout.addWidget(self.equil_vector_tabs)

        cell_origin_layout = QHBoxLayout()
        cell_origin_layout.addWidget(self.equil_cell_origin_label)
        cell_origin_layout.addWidget(self.equil_cell_origin_x_input)
        cell_origin_layout.addWidget(self.equil_cell_origin_y_input)
        cell_origin_layout.addWidget(self.equil_cell_origin_z_input)

        wrapping_water_layout = QHBoxLayout()
        wrapping_water_layout.addWidget(self.equil_wrapping_water_label)
        wrapping_water_layout.addWidget(self.equil_wrapping_water_combo)

        extra_label_layout = QHBoxLayout()
        extra_label_layout.addWidget(self.extra_label)
        extra_label_layout.addWidget(self.extra_input)




        main_layout = QVBoxLayout()
        main_layout.addLayout(psf_layout)
        main_layout.addLayout(coor_layout)
        main_layout.addLayout(vel_layout)
        main_layout.addLayout(extsystem_layout)
        main_layout.addLayout(param_layout)
        main_layout.addLayout(param_files_layout)
        main_layout.addLayout(exclude_layout)
        main_layout.addLayout(scaling_layout)
        main_layout.addLayout(dielectric_layout)
        main_layout.addLayout(switch_layout)
        main_layout.addLayout(cutoff_layout)
        main_layout.addLayout(pairlist_layout)
        main_layout.addLayout(margin_layout)
        main_layout.addLayout(stepspercycle_layout)
        main_layout.addLayout(rigidbonds_layout)
        main_layout.addLayout(rigid_tolerance_layout)
        main_layout.addLayout(rigid_iterations_layout)
        main_layout.addLayout(langevindynamics_layout)
        main_layout.addLayout(langevindamping_layout)
        main_layout.addLayout(langevintemp_layout)
        main_layout.addLayout(langevinhydrogen_layout)
        main_layout.addLayout(usegroup_pressure_layout)
        main_layout.addLayout(useflexiblecell_layout)
        main_layout.addLayout(useconstantarea_layout)
        main_layout.addLayout(langevinpiston_layout)
        main_layout.addLayout(langevinpistontarget_layout)
        main_layout.addLayout(langevinpistonperiod_layout)
        main_layout.addLayout(langevinpistondecay_layout)
        main_layout.addLayout(langevinpistontemp_layout)
        main_layout.addLayout(pme_layout)
        main_layout.addLayout(pme_tolerance_layout)
        main_layout.addLayout(pme_grid_layout)
        main_layout.addLayout(timestep_layout)
        main_layout.addLayout(fullelectfreq_layout)
        main_layout.addLayout(output_energies_layout)
        main_layout.addLayout(output_timing_layout)
        main_layout.addLayout(binary_output_layout)
        main_layout.addLayout(output_name_layout)
        main_layout.addLayout(restart_name_layout)
        main_layout.addLayout(restart_freq_layout)
        main_layout.addLayout(binary_restart_layout)
        main_layout.addLayout(dcd_file_layout)
        main_layout.addLayout(dcd_freq_layout)
        main_layout.addLayout(seed_layout)
        main_layout.addLayout(num_steps_layout)
        main_layout.addLayout(rescalefreq_layout)
        main_layout.addLayout(rescaletemp_layout)
        main_layout.addLayout(cell_basis_layout)
        main_layout.addLayout(cell_origin_layout)
        main_layout.addLayout(wrapping_water_layout)
        main_layout.addLayout(extra_label_layout)
        main_layout.addWidget(self.equilibrium_button)

        self.setLayout(main_layout)



        self.equil_param_files_label.setEnabled(False)
        self.equil_param_files_input.setEnabled(False)
        self.equil_param_files_button.setEnabled(False)

        
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle('Equilibration GUI')
        self.show()

    def toggleParamFiles(self):
        is_checked = self.equil_param_checkbox.isChecked()
        self.equil_param_files_label.setEnabled(is_checked)
        self.equil_param_files_input.setEnabled(is_checked)
        self.equil_param_files_button.setEnabled(is_checked)
        # Also update in other forms
        if hasattr(self, 'minimization_form') and self.minimization_form:
            self.minimization_form.min_param_checkbox.setChecked(is_checked)
            self.minimization_form.min_param_files_label.setEnabled(is_checked)
            self.minimization_form.min_param_files_input.setEnabled(is_checked)
            self.minimization_form.min_param_files_button.setEnabled(is_checked)
        if hasattr(self, 'heating_form') and self.heating_form:
            self.heating_form.heat_param_checkbox.setChecked(is_checked)
            self.heating_form.heat_param_files_label.setEnabled(is_checked)
            self.heating_form.heat_param_files_input.setEnabled(is_checked)
            self.heating_form.heat_param_files_button.setEnabled(is_checked)
        if hasattr(self, 'production_form') and self.production_form:
            self.production_form.param_checkbox.setChecked(is_checked)
            self.production_form.param_files_label.setEnabled(is_checked)
            self.production_form.param_files_input.setEnabled(is_checked)
            self.production_form.param_files_button.setEnabled(is_checked)

    def browseParamFiles(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, 'Open Parameter Files', '', 'All Files (*)')
        if file_names:
            self.selected_param_files = file_names
            self.equil_param_files_input.setText('\n '.join(file_names))

    def toggleSwitchDistance(self):
        is_checked = self.equil_switch_checkbox.isChecked()
        self.equil_switch_distance_input.setEnabled(is_checked)


    def submitForm(self):
        psf_file = self.equil_psf_input.text()
        coor_file = self.equil_coor_input.text()
        vel_file = self.equil_vel_input.text()
        extsystem_file = self.equil_extsystem_input.text()
        param_files = self.equil_param_files_input.text()
        exclude_scaled = self.equil_exclude_combo.currentText()
        scaling_value = self.equil_scaling_input.value()
        dielectric_constant = self.equil_dielectric_input.value()
        cutoff = self.equil_cutoff_input.value()
        pairlist_distance = self.equil_pairlist_distance_input.value()
        margin = self.equil_margin_input.value()
        stepspercycle = self.equil_stepspercycle_input.value()
        rigid_bonds = self.equil_rigidbonds_combo.currentText()
        rigid_tolerance = self.equil_rigid_tolerance_input.value()
        rigid_iterations = self.equil_rigid_iterations_input.value()
        pme_enabled = self.equil_pme_on_radio.isChecked()
        langevindynamics = self.equil_langevindynamics_combo.currentText()
        langevindamping = self.equil_langevin_damping_input.value()
        langevintemp = self.equil_langevintemp_input.value()
        langevinhydrogen = self.equil_langevinhydrogen_combo.currentText()
        usegroup_pressure = self.equil_usegroup_pressure_combo.currentText()
        useflexiblecell = self.equil_useflexiblecell_combo.currentText()
        useconstantarea = self.equil_useconstantarea_combo.currentText()
        langevinpiston = self.equil_langevinpiston_combo.currentText()
        langevinpistontarget = self.equil_langevinpistontarget_input.value()
        langevinpistonperiod = self.equil_langevinpistonperiod_input.value()
        langevinpistondecay = self.equil_langevinpistondecay_input.value()
        langevinpistontemp = self.equil_langevinpistontemp_input.value()
        pme_tolerance = self.equil_pme_tolerance_input.value()
        pme_grid_x = self.equil_pme_grid_x_input.value()
        pme_grid_y = self.equil_pme_grid_y_input.value()
        pme_grid_z = self.equil_pme_grid_z_input.value()
        timestep = self.equil_timestep_input.value()
        fullelectfreq = self.equil_fullelectfreq_input.value()
        output_energies = self.equil_output_energies_input.value()
        output_timing = self.equil_output_timing_input.value()
        binary_output = self.equil_binary_output_combo.currentText()
        output_name = self.equil_output_name_input.text()
        restart_name = self.equil_restart_name_input.text()
        restart_freq = self.equil_restart_freq_input.value()
        binary_restart = self.equil_binary_restart_combo.currentText()
        dcd_file = self.equil_dcd_file_input.text()
        dcd_freq = self.equil_dcd_freq_input.value()
        seed = self.equil_seed_input.value()
        num_steps = self.equil_num_steps_input.value()
        rescalefreq = self.equil_rescalefreq_input.value()
        rescaletemp = self.equil_rescaletemp_input.value()
        vector1_1 = self.equil_vector1_x_input.value()
        vector1_2 = self.equil_vector1_y_input.value()
        vector1_3 = self.equil_vector1_z_input.value()
        vector2_1 = self.equil_vector2_x_input.value()
        vector2_2 = self.equil_vector2_y_input.value()
        vector2_3 = self.equil_vector2_z_input.value()
        vector3_1 = self.equil_vector3_x_input.value()
        vector3_2 = self.equil_vector3_y_input.value()
        vector3_3 = self.equil_vector3_z_input.value()
        cell_origin_x = self.equil_cell_origin_x_input.value()
        cell_origin_y = self.equil_cell_origin_y_input.value()
        cell_origin_z = self.equil_cell_origin_z_input.value()
        wrapping_water = self.equil_wrapping_water_combo.currentText()
        extra_text = self.extra_input.toPlainText()

        if self.equil_param_checkbox.isChecked() and not param_files:
            QMessageBox.warning(self, 'Error', 'Please upload parameter files or disable paratypecharm.')
            return False

        if self.equil_switch_checkbox.isChecked():
            switch_distance = self.equil_switch_distance_input.value()
        else:
            switch_distance = None

        result = self.saveToFile(psf_file, coor_file, vel_file, extsystem_file, param_files, exclude_scaled, scaling_value, dielectric_constant, switch_distance, cutoff,
                        pairlist_distance, margin, stepspercycle, rigid_bonds,
                        rigid_tolerance, rigid_iterations, langevindynamics, langevindamping, langevinhydrogen, langevintemp, usegroup_pressure,
                        useconstantarea, useflexiblecell, langevinpiston, langevinpistonperiod, langevinpistondecay, langevinpistontarget, langevinpistontemp,
                        pme_enabled, pme_tolerance, pme_grid_x, pme_grid_y,
                        pme_grid_z, output_energies, timestep, fullelectfreq, output_timing, binary_output,
                        output_name, restart_name, restart_freq, binary_restart, dcd_file, dcd_freq, seed,
                        num_steps, rescalefreq, rescaletemp, vector1_1, vector1_2, vector1_3, vector2_1,
                        vector2_2, vector2_3, vector3_1, vector3_2, vector3_3, cell_origin_x, cell_origin_y,
                        cell_origin_z, wrapping_water, extra_text)

        if result:
            print('Your simulation parameters are saved to configuration file.')
            QMessageBox.information(self, 'Success', 'Your simulation parameters are saved to configuration file.')
        return result

    def saveToFile(self, psf_file, coor_file, vel_file, extsystem_file, param_files, exclude_scaled, scaling_value, dielectric_constant, switch_distance, cutoff,
                   pairlist_distance, margin, stepspercycle, rigid_bonds,
                   rigid_tolerance, rigid_iterations, langevindynamics, langevindamping, langevinhydrogen, langevintemp, usegroup_pressure,
                   useconstantarea, useflexiblecell, langevinpiston, langevinpistonperiod, langevinpistondecay, langevinpistontarget,
                   langevinpistontemp, pme_enabled, pme_tolerance, pme_grid_x, pme_grid_y, pme_grid_z,
                   output_energies, timestep, fullelectfreq, output_timing, binary_output,
                   output_name, restart_name, restart_freq, binary_restart, dcd_file, dcd_freq, seed, num_steps,
                   rescalefreq, rescaletemp, vector1_1, vector1_2, vector1_3, vector2_1, vector2_2,
                   vector2_3, vector3_1, vector3_2, vector3_3, cell_origin_x, cell_origin_y, cell_origin_z,
                   wrapping_water, extra_text):


        default_name = 'equilibration.conf'
        if hasattr(self, 'directory_setup_tab') and self.directory_setup_tab:
            save_dir = self.directory_setup_tab.get_directory()
            if save_dir:
                default_path = os.path.join(save_dir, default_name)
            else:
                default_path = default_name
        else:
            default_path = default_name

        file_name_eq, selected_filter = QFileDialog.getSaveFileName(self, 'Save Configuration File', default_path, 'All Files (*);;Config Files/Inp Files (*.conf *.inp)')
        if not file_name_eq:
            return False
        
        if '.' not in file_name_eq:
            if 'conf' in selected_filter:
                file_name_eq += '.conf'
            elif 'inp' in selected_filter:
                file_name_eq += '.inp'
            else:
                file_name_eq += '.conf'

        with open(file_name_eq, 'w') as file:
            file.write("##############################################\n")
            file.write("#### input topology and initial structure ####\n")
            file.write("##############################################\n")
            file.write(f'structure             {psf_file}\n')
            file.write(f'coordinates           {coor_file}\n')
            file.write(f'velocities            {vel_file}\n')
            file.write(f'extendedsystem        {extsystem_file}\n\n\n')

            file.write("##############################################\n")
            file.write("#### force field block #######################\n")
            file.write("##############################################\n\n")
            file.write(f'paratypecharmm        on\n')
            for param_files in self.selected_param_files:
                file.write(f'parameters        {os.path.basename(param_files)}\n')
            file.write(f'exclude               {exclude_scaled}\n\n\n')
            file.write(f'1-4scaling           {scaling_value}\n')
            file.write(f'dielectric            {dielectric_constant}\n\n')

            file.write("##############################################\n")
            file.write("### dealing with long-range interactions######\n")
            file.write("##############################################\n\n")
            file.write(f'switching             on \n')
            file.write(f'switchdist            {switch_distance}\n')
            file.write(f'cutoff                {cutoff}\n')
            file.write(f'pairlistdist          {pairlist_distance}\n')
            file.write(f'margin                {margin}\n')
            file.write(f'stepspercycle         {stepspercycle}\n')
            file.write(f'rigidBonds            {rigid_bonds}\n')
            file.write(f'rigidTolerance        {rigid_tolerance:.6f}\n')
            file.write(f'rigidIterations       {rigid_iterations}\n\n\n')

            file.write("##############################################\n")
            file.write("###### Constant Temperature Control ##########\n")
            file.write("##############################################\n\n")
            file.write(f'langevin              {langevindynamics}\n')
            file.write(f'langevinDamping       {langevindamping}\n')
            file.write(f'langevinTemp          {langevintemp}\n')
            file.write(f'langevinHydrogen      {langevinhydrogen}\n\n\n')

            file.write("##############################################\n")
            file.write("###### Constant Pressure Control #############\n")
            file.write("##############################################\n\n")
            file.write(f'useGroupPressure           {usegroup_pressure}\n')
            file.write(f'useFlexibleCell            {useflexiblecell}\n')
            file.write(f'useConstantArea            {useconstantarea}\n\n')
            file.write(f'langevinPiston              {langevinpiston}\n')
            file.write(f'langevinPistonTarget        {langevinpistontarget:.6f}\n')
            file.write(f'langevinPistonPeriod        {langevinpistonperiod}\n')
            file.write(f'langevinPistonDecay         {langevinpistondecay}\n')            
            file.write(f'langevinPistonTemp          {langevinpistontemp}\n\n\n')

            file.write("##############################################\n")
            file.write("###### Ewald electrostatics ##################\n")
            file.write("##############################################\n\n")
            file.write(f'PME                {"on" if pme_enabled else "off"}\n')
            file.write(f'PMETolerance       {pme_tolerance:.6f}\n')
            file.write(f'PMEGridSizeX       {pme_grid_x}\n')
            file.write(f'PMEGridSizeY       {pme_grid_y}\n')
            file.write(f'PMEGridSizeZ       {pme_grid_z}\n\n\n')

            file.write("##############################################\n")
            file.write("###### parameters for integrator and MTS #####\n")
            file.write("##############################################\n\n")
            file.write(f'timestep                 {timestep}\n')
            file.write(f'fullElectFrequency       {fullelectfreq}\n\n\n')

            file.write("##############################################\n")
            file.write("###### the output ############################\n")
            file.write("##############################################\n\n")
            file.write(f'outputenergies           {output_energies}\n')
            file.write(f'outputtiming             {output_timing}\n')
            file.write(f'binaryoutput             {binary_output}\n')
            file.write(f'outputname               {output_name}\n')
            file.write(f'restartname              {restart_name}\n')
            file.write(f'restartfreq              {restart_freq}\n')
            file.write(f'binaryrestart            {binary_restart}\n')
            file.write(f'DCDfile                  {dcd_file}\n')
            file.write(f'dcdfreq                  {dcd_freq}\n\n\n')
            if extra_text:
                file.write(f'{extra_text}\n')

            file.write("##############################################\n")
            file.write("###### MD protocol block #####################\n")
            file.write("##############################################\n\n")
            file.write(f'seed               {seed}\n')
            file.write(f'numsteps           {num_steps}\n')
            file.write(f'rescaleFreq        {rescalefreq}\n')
            file.write(f'rescaleTemp        {rescaletemp}\n')

            file.write("#########################################################\n")
            file.write("# this block defines periodic boundary conditions #######\n")
            file.write("#########################################################\n")
            file.write(f'cellBasisVector1         {vector1_1} {vector1_2} {vector1_3}\n')
            file.write(f'cellBasisVector2         {vector2_1} {vector2_2} {vector2_3}\n')
            file.write(f'cellBasisVector3         {vector3_1} {vector3_2} {vector3_3}\n')
            file.write(f'cellOrigin               {cell_origin_x} {cell_origin_y} {cell_origin_z}\n\n')
            file.write(f'wrapWater                {wrapping_water}\n')
            
        return True

    def equilibriumAction(self):
        result = self.submitForm()
        if result:
            print('Equilibration file generated successfully.')
            QMessageBox.information(self, 'Equilibration', 'Equilibration file generated successfully.')



class ProductionGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_param_files = []

    def initUI(self):
        

        self.psf_label = QLabel('PSF File', self)
        self.psf_input = QLineEdit(self)

        self.coor_label = QLabel('Coordinate File', self)
        self.coor_input = QLineEdit(self)
        self.coor_input.setText("Complex_equil.coor")

        self.vel_label = QLabel('Velocity File', self)
        self.vel_input = QLineEdit(self)
        self.vel_input.setText("Complex_equil.vel")

        self.extsystem_label = QLabel('Extended System File', self)
        self.extsystem_input = QLineEdit(self)
        self.extsystem_input.setText("Complex_equil.xsc")

        self.param_checkbox = QCheckBox('Paratype-CHARMM', self)
        self.param_checkbox.stateChanged.connect(self.toggleParamFiles)

        self.param_files_label = QLabel('Parameter Files', self)
        self.param_files_input = QLineEdit(self)
        self.param_files_button = QPushButton('Browse', self)
        self.param_files_button.clicked.connect(self.browseParamFiles)

        self.exclude_label = QLabel('Exclude Scaled', self)
        self.exclude_combo = QComboBox(self)
        self.exclude_combo.addItems(['none', 'scaled1-4'])

        self.scaling_label = QLabel('1-4 Scaling', self)
        self.scaling_input = QDoubleSpinBox(self)
        self.scaling_input.setRange(0, 1.0)

        self.dielectric_label = QLabel('Dielectric', self)
        self.dielectric_input = QDoubleSpinBox(self)
        self.dielectric_input.setRange(0, 1.0)

        self.switch_checkbox = QCheckBox('Enable Switching', self)
        self.switch_checkbox.stateChanged.connect(self.toggleSwitchDistance)

        self.switch_distance_label = QLabel('Switch Distance', self)
        self.switch_distance_input = QDoubleSpinBox(self)
        self.switch_distance_input.setRange(0.0, 12.0)
        self.switch_distance_input.setDecimals(1)
        self.switch_distance_input.setEnabled(False)

        self.cutoff_label = QLabel('Cut-off', self)
        self.cutoff_input = QDoubleSpinBox(self)
        self.cutoff_input.setRange(0.0, 30.0)
        
        self.pairlist_distance_label = QLabel('Pairlist Distance', self)
        self.pairlist_distance_input = QDoubleSpinBox(self)
        self.pairlist_distance_input.setDecimals(2)
        self.pairlist_distance_input.setRange(0.0, 100.0)

        self.margin_label = QLabel('Margin', self)
        self.margin_input = QDoubleSpinBox(self)
        self.margin_input.setDecimals(2)
        self.margin_input.setRange(0.0, 10.0)

        self.stepspercycle_label = QLabel('Steps per cycle', self)
        self.stepspercycle_input = QSpinBox(self)
        self.stepspercycle_input.setRange(0, 50)

        self.rigidbonds_label = QLabel('Rigid bonds', self)
        self.rigidbonds_combo = QComboBox(self)
        self.rigidbonds_combo.addItems(['all', 'none'])
        self.rigidbonds_combo.setCurrentIndex(0)

        self.rigid_tolerance_label = QLabel('Rigid Tolerance', self)
        self.rigid_tolerance_input = QDoubleSpinBox(self)
        self.rigid_tolerance_input.setDecimals(5)
        self.rigid_tolerance_input.setRange(0.0, 1.0)

        self.rigid_iterations_label = QLabel('Rigid Iterations', self)
        self.rigid_iterations_input = QSpinBox(self)
        self.rigid_iterations_input.setRange(0, 100000)

        self.langevindynamics_label = QLabel('Langevin Dynamics', self)
        self.langevindynamics_combo = QComboBox(self)
        self.langevindynamics_combo.addItems(['on', 'off'])
        self.langevindynamics_combo.setCurrentIndex(0)

        self.langevin_damping_label = QLabel('Langevin Damping', self)
        self.langevin_damping_input = QSpinBox(self)
        self.langevin_damping_input.setRange(0,2)
        self.langevin_damping_input.setValue(1)

        self.langevintemp_label = QLabel('Langevin Temperature', self)
        self.langevintemp_input = QSpinBox(self)
        self.langevintemp_input.setRange(0,100000)
        self.langevintemp_input.setValue(300)

        self.langevinhydrogen_label = QLabel('Langevin Hydrogen', self)
        self.langevinhydrogen_combo = QComboBox(self)
        self.langevinhydrogen_combo.addItems(['on', 'off'])
        self.langevinhydrogen_combo.setCurrentIndex(1)

        self.usegroup_pressure_label = QLabel('Use Group Pressure', self)
        self.usegroup_pressure_combo = QComboBox(self)
        self.usegroup_pressure_combo.addItems(['yes', 'no'])
        self.usegroup_pressure_combo.setCurrentIndex(0)

        self.useflexiblecell_label = QLabel('Use Flexible Cell', self)
        self.useflexiblecell_combo = QComboBox(self)
        self.useflexiblecell_combo.addItems(['yes', 'no'])
        self.useflexiblecell_combo.setCurrentIndex(1)

        self.useconstantarea_label = QLabel('Use Constant Area', self)
        self.useconstantarea_combo = QComboBox(self)
        self.useconstantarea_combo.addItems(['yes', 'no'])
        self.useconstantarea_combo.setCurrentIndex(1)

        self.langevinpiston_label = QLabel('Langevin Piston', self)
        self.langevinpiston_combo = QComboBox(self)
        self.langevinpiston_combo.addItems(['off', 'on'])
        self.langevinpiston_combo.setCurrentIndex(1)

        self.langevinpistontarget_label = QLabel('Langevin Piston Target', self)
        self.langevinpistontarget_input = QDoubleSpinBox(self)
        self.langevinpistontarget_input.setDecimals(5)
        self.langevinpistontarget_input.setValue(1.01325)
        self.langevinpistontarget_input.setRange(0.0, 10.0)

        self.langevinpistonperiod_label = QLabel('Langevin Piston Period', self)
        self.langevinpistonperiod_input = QSpinBox(self)
        self.langevinpistonperiod_input.setRange(0, 500)
        self.langevinpistonperiod_input.setValue(100)

        self.langevinpistondecay_label = QLabel('Langevin Piston Decay', self)
        self.langevinpistondecay_input = QDoubleSpinBox(self)
        self.langevinpistondecay_input.setDecimals(2)
        self.langevinpistondecay_input.setValue(50)
        self.langevinpistondecay_input.setRange(0.0, 100.0)

        self.langevinpistontemp_label = QLabel('Langevin Piston Temperature', self)
        self.langevinpistontemp_input = QSpinBox(self)
        self.langevinpistontemp_input.setRange(0,500)
        self.langevinpistontemp_input.setValue(300)
        self.langevinpistontemp_input.setRange(0,1000)

        self.pme_label = QLabel('PME', self)
        self.pme_on_radio = QRadioButton('On', self)
        self.pme_off_radio = QRadioButton('Off', self)
        self.pme_on_radio.setChecked(True)

        self.pme_tolerance_label = QLabel('PME Tolerance', self)
        self.pme_tolerance_input = QDoubleSpinBox(self)
        self.pme_tolerance_input.setDecimals(6)
        self.pme_tolerance_input.setValue(0.000001)
        self.pme_tolerance_input.setRange(0.0, 1.0)

        self.pme_grid_x_label = QLabel('PME Grid Size X', self)
        self.pme_grid_x_input = QSpinBox(self)
        self.pme_grid_x_input.setRange(1, 512)
        
        self.pme_grid_y_label = QLabel('PME Grid Size Y', self)
        self.pme_grid_y_input = QSpinBox(self)
        self.pme_grid_y_input.setRange(1, 512)
        
        self.pme_grid_z_label = QLabel('PME Grid Size Z', self)
        self.pme_grid_z_input = QSpinBox(self)
        self.pme_grid_z_input.setRange(1, 512)
        
        self.timestep_label = QLabel('Time Step', self)
        self.timestep_input = QDoubleSpinBox(self)
        self.timestep_input.setRange(1, 2)
        self.timestep_input.setValue(2)

        self.fullelectfreq_label = QLabel('Full Electrostatics Frequency', self)
        self.fullelectfreq_input = QSpinBox(self)
        self.fullelectfreq_input.setRange(1, 100)
        self.fullelectfreq_input.setValue(4)

        self.output_energies_label = QLabel('Output Energies', self)
        self.output_energies_input = QSpinBox(self)
        self.output_energies_input.setRange(0, 1000000)
        self.output_energies_input.setValue(50000)

        self.output_timing_label = QLabel('Output Timing', self)
        self.output_timing_input = QSpinBox(self)
        self.output_timing_input.setRange(0, 1000000)
        self.output_timing_input.setValue(50000)

        self.binary_output_label = QLabel('Binary Output', self)
        self.binary_output_combo = QComboBox(self)
        self.binary_output_combo.addItems(['yes', 'no'])
        self.binary_output_combo.setCurrentIndex(1)

        self.output_name_label = QLabel('Output Name', self)
        self.output_name_input = QLineEdit(self)
        self.output_name_input.setText("Complex_prod")

        self.restart_name_label = QLabel('Restart Name', self)
        self.restart_name_input = QLineEdit(self)
        self.restart_name_input.setText("Complex_prod_restart")

        self.restart_freq_label = QLabel('Restart Frequency', self)
        self.restart_freq_input = QSpinBox(self)
        self.restart_freq_input.setRange(0, 100000000)
        self.restart_freq_input.setValue(50000)

        self.binary_restart_label = QLabel('Binary Restart', self)
        self.binary_restart_combo = QComboBox(self)
        self.binary_restart_combo.addItems(['yes', 'no'])
        self.binary_restart_combo.setCurrentIndex(1)

        self.dcd_file_label = QLabel('DCD File', self)
        self.dcd_file_input = QLineEdit(self)
        self.dcd_file_input.setText("Complex_prod.dcd")

        self.dcd_freq_label = QLabel('DCD Frequency', self)
        self.dcd_freq_input = QSpinBox(self)
        self.dcd_freq_input.setRange(0, 1000000000)
        self.dcd_freq_input.setValue(50000)

        self.seed_label = QLabel('Seed', self)
        self.seed_input = QSpinBox(self)
        self.seed_input.setRange(1, 10000)
        self.seed_input.setValue(3010)

        self.num_steps_label = QLabel('Number of Steps', self)
        self.num_steps_input = QSpinBox(self)
        self.num_steps_input.setRange(0, 1000000000)
        self.num_steps_input.setValue(50000000)
        
        self.cell_basis_vector_label = QLabel("Cell Basis Vectors", self)

        self.vector_tabs = QTabWidget()
        self.vector1_tab = QWidget()
        self.vector2_tab = QWidget()
        self.vector3_tab = QWidget()

        self.vector1_x_input = QDoubleSpinBox(self)
        self.vector1_x_input.setDecimals(3)
        self.vector1_x_input.setRange(-999.999, 999.999)
        
        self.vector1_y_input = QDoubleSpinBox(self)
        self.vector1_y_input.setDecimals(3)
        self.vector1_y_input.setRange(-999.999, 999.999)
        self.vector1_z_input = QDoubleSpinBox(self)
        self.vector1_z_input.setDecimals(3)
        self.vector1_z_input.setRange(-999.999, 999.999)

        vector1_layout = QHBoxLayout()
        vector1_layout.addWidget(QLabel("X:"))
        vector1_layout.addWidget(self.vector1_x_input)
        vector1_layout.addWidget(QLabel("Y:"))
        vector1_layout.addWidget(self.vector1_y_input)
        vector1_layout.addWidget(QLabel("Z:"))
        vector1_layout.addWidget(self.vector1_z_input)
        self.vector1_tab.setLayout(vector1_layout)

        self.vector2_x_input = QDoubleSpinBox(self)
        self.vector2_x_input.setDecimals(3)
        self.vector2_x_input.setRange(-999.999, 999.999)
        self.vector2_y_input = QDoubleSpinBox(self)
        self.vector2_y_input.setDecimals(3)
        self.vector2_y_input.setRange(-999.999, 999.999)
        self.vector2_z_input = QDoubleSpinBox(self)
        self.vector2_z_input.setDecimals(3)
        self.vector2_z_input.setRange(-999.999, 999.999)

        vector2_layout = QHBoxLayout()
        vector2_layout.addWidget(QLabel("X:"))
        vector2_layout.addWidget(self.vector2_x_input)
        vector2_layout.addWidget(QLabel("Y:"))
        vector2_layout.addWidget(self.vector2_y_input)
        vector2_layout.addWidget(QLabel("Z:"))
        vector2_layout.addWidget(self.vector2_z_input)
        self.vector2_tab.setLayout(vector2_layout)

        self.vector3_x_input = QDoubleSpinBox(self)
        self.vector3_x_input.setDecimals(3)
        self.vector3_x_input.setRange(-999.999, 999.999)
        self.vector3_y_input = QDoubleSpinBox(self)
        self.vector3_y_input.setDecimals(3)
        self.vector3_y_input.setRange(-999.999, 999.999)
        self.vector3_z_input = QDoubleSpinBox(self)
        self.vector3_z_input.setDecimals(3)
        self.vector3_z_input.setRange(-999.999, 999.999)

        vector3_layout = QHBoxLayout()
        vector3_layout.addWidget(QLabel("X:"))
        vector3_layout.addWidget(self.vector3_x_input)
        vector3_layout.addWidget(QLabel("Y:"))
        vector3_layout.addWidget(self.vector3_y_input)
        vector3_layout.addWidget(QLabel("Z:"))
        vector3_layout.addWidget(self.vector3_z_input)
        self.vector3_tab.setLayout(vector3_layout)

        self.vector_tabs.addTab(self.vector1_tab, "Cell Basis Vector 1")
        self.vector_tabs.addTab(self.vector2_tab, "Cell Basis Vector 2")
        self.vector_tabs.addTab(self.vector3_tab, "Cell Basis Vector 3")

        self.cell_origin_label = QLabel("Cell Origin", self)

        self.cell_origin_x_input = QDoubleSpinBox(self)
        self.cell_origin_x_input.setDecimals(18)
        self.cell_origin_x_input.setRange(-999.999999999999999999, 999.999999999999999999)

        self.cell_origin_y_input = QDoubleSpinBox(self)
        self.cell_origin_y_input.setDecimals(18)
        self.cell_origin_y_input.setRange(-999.999999999999999999, 999.999999999999999999)
        
        self.cell_origin_z_input = QDoubleSpinBox(self)
        self.cell_origin_z_input.setDecimals(18)
        self.cell_origin_z_input.setRange(-999.999999999999999999, 999.999999999999999999)

        self.wrapping_water_combo = QComboBox(self)
        self.wrapping_water_label = QLabel('Wrapping Water', self)
        self.wrapping_water_combo.addItems(['on', 'off'])
        self.wrapping_water_combo.setCurrentIndex(0)

        self.extra_label = QLabel("User defined simulation parameters", self)
        self.extra_input = QTextEdit(self)
        self.extra_input.setPlaceholderText("Enter parameters here if necessary...")

        self.production_button = QPushButton('Create Production Configuration file', self)
        self.production_button.clicked.connect(self.productionAction)
        

        psf_layout = QHBoxLayout()
        psf_layout.addWidget(self.psf_label)
        psf_layout.addWidget(self.psf_input)

        coor_layout = QHBoxLayout()
        coor_layout.addWidget(self.coor_label)
        coor_layout.addWidget(self.coor_input)

        vel_layout = QHBoxLayout()
        vel_layout.addWidget(self.vel_label)
        vel_layout.addWidget(self.vel_input)
    
        extsystem_layout = QHBoxLayout()
        extsystem_layout.addWidget(self.extsystem_label)
        extsystem_layout.addWidget(self.extsystem_input)
        
        param_layout = QHBoxLayout()
        param_layout.addWidget(self.param_checkbox)

        param_files_layout = QHBoxLayout()
        param_files_layout.addWidget(self.param_files_label)
        param_files_layout.addWidget(self.param_files_input)
        param_files_layout.addWidget(self.param_files_button)

        exclude_layout = QHBoxLayout()
        exclude_layout.addWidget(self.exclude_label)
        exclude_layout.addWidget(self.exclude_combo)

        scaling_layout = QHBoxLayout()
        scaling_layout.addWidget(self.scaling_label)
        scaling_layout.addWidget(self.scaling_input)

        dielectric_layout = QHBoxLayout()
        dielectric_layout.addWidget(self.dielectric_label)
        dielectric_layout.addWidget(self.dielectric_input)

        switch_layout = QHBoxLayout()
        switch_layout.addWidget(self.switch_checkbox)
        switch_layout.addWidget(self.switch_distance_label)
        switch_layout.addWidget(self.switch_distance_input)

        cutoff_layout = QHBoxLayout()
        cutoff_layout.addWidget(self.cutoff_label)
        cutoff_layout.addWidget(self.cutoff_input)

        pairlist_layout = QHBoxLayout()
        pairlist_layout.addWidget(self.pairlist_distance_label)
        pairlist_layout.addWidget(self.pairlist_distance_input)

        margin_layout = QHBoxLayout()
        margin_layout.addWidget(self.margin_label)
        margin_layout.addWidget(self.margin_input)

        stepspercycle_layout = QHBoxLayout()
        stepspercycle_layout.addWidget(self.stepspercycle_label)
        stepspercycle_layout.addWidget(self.stepspercycle_input)

        rigidbonds_layout = QHBoxLayout()
        rigidbonds_layout.addWidget(self.rigidbonds_label)
        rigidbonds_layout.addWidget(self.rigidbonds_combo)

        rigid_tolerance_layout = QHBoxLayout()
        rigid_tolerance_layout.addWidget(self.rigid_tolerance_label)
        rigid_tolerance_layout.addWidget(self.rigid_tolerance_input)

        rigid_iterations_layout = QHBoxLayout()
        rigid_iterations_layout.addWidget(self.rigid_iterations_label)
        rigid_iterations_layout.addWidget(self.rigid_iterations_input)

        langevindynamics_layout = QHBoxLayout()
        langevindynamics_layout.addWidget(self.langevindynamics_label)
        langevindynamics_layout.addWidget(self.langevindynamics_combo)

        langevindamping_layout = QHBoxLayout()
        langevindamping_layout.addWidget(self.langevin_damping_label)
        langevindamping_layout.addWidget(self.langevin_damping_input)

        langevintemp_layout = QHBoxLayout()
        langevintemp_layout.addWidget(self.langevintemp_label)
        langevintemp_layout.addWidget(self.langevintemp_input)

        langevinhydrogen_layout = QHBoxLayout()
        langevinhydrogen_layout.addWidget(self.langevinhydrogen_label)
        langevinhydrogen_layout.addWidget(self.langevinhydrogen_combo)

        usegroup_pressure_layout = QHBoxLayout()
        usegroup_pressure_layout.addWidget(self.usegroup_pressure_label)
        usegroup_pressure_layout.addWidget(self.usegroup_pressure_combo)

        useflexiblecell_layout = QHBoxLayout()
        useflexiblecell_layout.addWidget(self.useflexiblecell_label)
        useflexiblecell_layout.addWidget(self.useflexiblecell_combo)

        useconstantarea_layout = QHBoxLayout()
        useconstantarea_layout.addWidget(self.useconstantarea_label)
        useconstantarea_layout.addWidget(self.useconstantarea_combo)

        langevinpiston_layout = QHBoxLayout()
        langevinpiston_layout.addWidget(self.langevinpiston_label)
        langevinpiston_layout.addWidget(self.langevinpiston_combo)

        langevinpistontarget_layout = QHBoxLayout()
        langevinpistontarget_layout.addWidget(self.langevinpistontarget_label)
        langevinpistontarget_layout.addWidget(self.langevinpistontarget_input)

        langevinpistonperiod_layout = QHBoxLayout()
        langevinpistonperiod_layout.addWidget(self.langevinpistonperiod_label)
        langevinpistonperiod_layout.addWidget(self.langevinpistonperiod_input)

        langevinpistondecay_layout = QHBoxLayout()
        langevinpistondecay_layout.addWidget(self.langevinpistondecay_label)
        langevinpistondecay_layout.addWidget(self.langevinpistondecay_input)

        langevinpistontemp_layout = QHBoxLayout()
        langevinpistontemp_layout.addWidget(self.langevinpistontemp_label)
        langevinpistontemp_layout.addWidget(self.langevinpistontemp_input)

        pme_layout = QVBoxLayout()
        pme_radio_layout = QHBoxLayout()
        pme_radio_layout.addWidget(self.pme_on_radio)
        pme_radio_layout.addWidget(self.pme_off_radio)
        pme_layout.addWidget(self.pme_label)
        pme_layout.addLayout(pme_radio_layout)

        pme_tolerance_layout = QHBoxLayout()
        pme_tolerance_layout.addWidget(self.pme_tolerance_label)
        pme_tolerance_layout.addWidget(self.pme_tolerance_input)

        pme_grid_layout = QVBoxLayout()

        pme_grid_x_layout = QHBoxLayout()
        pme_grid_x_layout.addWidget(self.pme_grid_x_label)
        pme_grid_x_layout.addWidget(self.pme_grid_x_input)
        pme_grid_layout.addLayout(pme_grid_x_layout)

        pme_grid_y_layout = QHBoxLayout()
        pme_grid_y_layout.addWidget(self.pme_grid_y_label)
        pme_grid_y_layout.addWidget(self.pme_grid_y_input)
        pme_grid_layout.addLayout(pme_grid_y_layout)

        pme_grid_z_layout = QHBoxLayout()
        pme_grid_z_layout.addWidget(self.pme_grid_z_label)
        pme_grid_z_layout.addWidget(self.pme_grid_z_input)
        pme_grid_layout.addLayout(pme_grid_z_layout)

        timestep_layout = QHBoxLayout()
        timestep_layout.addWidget(self.timestep_label)
        timestep_layout.addWidget(self.timestep_input)

        fullelectfreq_layout = QHBoxLayout()
        fullelectfreq_layout.addWidget(self.fullelectfreq_label)
        fullelectfreq_layout.addWidget(self.fullelectfreq_input)

        output_energies_layout = QHBoxLayout()
        output_energies_layout.addWidget(self.output_energies_label)
        output_energies_layout.addWidget(self.output_energies_input)

        output_timing_layout = QHBoxLayout()
        output_timing_layout.addWidget(self.output_timing_label)
        output_timing_layout.addWidget(self.output_timing_input)

        binary_output_layout = QHBoxLayout()
        binary_output_layout.addWidget(self.binary_output_label)
        binary_output_layout.addWidget(self.binary_output_combo)

        output_name_layout = QHBoxLayout()
        output_name_layout.addWidget(self.output_name_label)
        output_name_layout.addWidget(self.output_name_input)

        restart_name_layout = QHBoxLayout()
        restart_name_layout.addWidget(self.restart_name_label)
        restart_name_layout.addWidget(self.restart_name_input)

        restart_freq_layout = QHBoxLayout()
        restart_freq_layout.addWidget(self.restart_freq_label)
        restart_freq_layout.addWidget(self.restart_freq_input)

        binary_restart_layout = QHBoxLayout()
        binary_restart_layout.addWidget(self.binary_restart_label)
        binary_restart_layout.addWidget(self.binary_restart_combo)

        dcd_file_layout = QHBoxLayout()
        dcd_file_layout.addWidget(self.dcd_file_label)
        dcd_file_layout.addWidget(self.dcd_file_input)

        dcd_freq_layout = QHBoxLayout()
        dcd_freq_layout.addWidget(self.dcd_freq_label)
        dcd_freq_layout.addWidget(self.dcd_freq_input)

        seed_layout = QHBoxLayout()
        seed_layout.addWidget(self.seed_label)
        seed_layout.addWidget(self.seed_input)

        num_steps_layout = QHBoxLayout()
        num_steps_layout.addWidget(self.num_steps_label)
        num_steps_layout.addWidget(self.num_steps_input)
        
        cell_basis_layout = QVBoxLayout()
        cell_basis_layout.addWidget(self.cell_basis_vector_label)
        cell_basis_layout.addWidget(self.vector_tabs)

        cell_origin_layout = QHBoxLayout()
        cell_origin_layout.addWidget(self.cell_origin_label)
        cell_origin_layout.addWidget(self.cell_origin_x_input)
        cell_origin_layout.addWidget(self.cell_origin_y_input)
        cell_origin_layout.addWidget(self.cell_origin_z_input)

        wrapping_water_layout = QHBoxLayout()
        wrapping_water_layout.addWidget(self.wrapping_water_label)
        wrapping_water_layout.addWidget(self.wrapping_water_combo)

        extra_label_layout = QHBoxLayout()
        extra_label_layout.addWidget(self.extra_label)
        extra_label_layout.addWidget(self.extra_input)


        main_layout = QVBoxLayout()
        main_layout.addLayout(psf_layout)
        main_layout.addLayout(coor_layout)
        main_layout.addLayout(vel_layout)
        main_layout.addLayout(extsystem_layout)
        main_layout.addLayout(param_layout)
        main_layout.addLayout(param_files_layout)
        main_layout.addLayout(exclude_layout)
        main_layout.addLayout(scaling_layout)
        main_layout.addLayout(dielectric_layout)
        main_layout.addLayout(switch_layout)
        main_layout.addLayout(cutoff_layout)
        main_layout.addLayout(pairlist_layout)
        main_layout.addLayout(margin_layout)
        main_layout.addLayout(stepspercycle_layout)
        main_layout.addLayout(rigidbonds_layout)
        main_layout.addLayout(rigid_tolerance_layout)
        main_layout.addLayout(rigid_iterations_layout)
        main_layout.addLayout(langevindynamics_layout)
        main_layout.addLayout(langevindamping_layout)
        main_layout.addLayout(langevintemp_layout)
        main_layout.addLayout(langevinhydrogen_layout)
        main_layout.addLayout(usegroup_pressure_layout)
        main_layout.addLayout(useflexiblecell_layout)
        main_layout.addLayout(useconstantarea_layout)
        main_layout.addLayout(langevinpiston_layout)
        main_layout.addLayout(langevinpistontarget_layout)
        main_layout.addLayout(langevinpistonperiod_layout)
        main_layout.addLayout(langevinpistondecay_layout)
        main_layout.addLayout(langevinpistontemp_layout)
        main_layout.addLayout(pme_layout)
        main_layout.addLayout(pme_tolerance_layout)
        main_layout.addLayout(pme_grid_layout)
        main_layout.addLayout(timestep_layout)
        main_layout.addLayout(fullelectfreq_layout)
        main_layout.addLayout(output_energies_layout)
        main_layout.addLayout(output_timing_layout)
        main_layout.addLayout(binary_output_layout)
        main_layout.addLayout(output_name_layout)
        main_layout.addLayout(restart_name_layout)
        main_layout.addLayout(restart_freq_layout)
        main_layout.addLayout(binary_restart_layout)
        main_layout.addLayout(dcd_file_layout)
        main_layout.addLayout(dcd_freq_layout)
        main_layout.addLayout(seed_layout)
        main_layout.addLayout(num_steps_layout)
        main_layout.addLayout(cell_basis_layout)
        main_layout.addLayout(cell_origin_layout)
        main_layout.addLayout(wrapping_water_layout)
        main_layout.addLayout(extra_label_layout)
        main_layout.addWidget(self.production_button)

        self.setLayout(main_layout)



        self.param_files_label.setEnabled(False)
        self.param_files_input.setEnabled(False)
        self.param_files_button.setEnabled(False)

        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle('Equilibration GUI')
        self.show()

    def toggleParamFiles(self):
        is_checked = self.param_checkbox.isChecked()
        self.param_files_label.setEnabled(is_checked)
        self.param_files_input.setEnabled(is_checked)
        self.param_files_button.setEnabled(is_checked)
        # Also update in other forms
        if hasattr(self, 'minimization_form') and self.minimization_form:
            self.minimization_form.min_param_checkbox.setChecked(is_checked)
            self.minimization_form.min_param_files_label.setEnabled(is_checked)
            self.minimization_form.min_param_files_input.setEnabled(is_checked)
            self.minimization_form.min_param_files_button.setEnabled(is_checked)
        if hasattr(self, 'heating_form') and self.heating_form:
            self.heating_form.heat_param_checkbox.setChecked(is_checked)
            self.heating_form.heat_param_files_label.setEnabled(is_checked)
            self.heating_form.heat_param_files_input.setEnabled(is_checked)
            self.heating_form.heat_param_files_button.setEnabled(is_checked)
        if hasattr(self, 'equilibrium_form') and self.equilibrium_form:
            self.equilibrium_form.equil_param_checkbox.setChecked(is_checked)
            self.equilibrium_form.equil_param_files_label.setEnabled(is_checked)
            self.equilibrium_form.equil_param_files_input.setEnabled(is_checked)
            self.equilibrium_form.equil_param_files_button.setEnabled(is_checked)

    def browseParamFiles(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, 'Open Parameter Files', '', 'All Files (*)')
        if file_names:
            self.selected_param_files = file_names
            self.param_files_input.setText('\n '.join(file_names))

    def toggleSwitchDistance(self):
        is_checked = self.switch_checkbox.isChecked()
        self.switch_distance_input.setEnabled(is_checked)



    def submitForm(self):
        psf_file = self.psf_input.text()
        coor_file = self.coor_input.text()
        vel_file = self.vel_input.text()
        extsystem_file = self.extsystem_input.text()
        param_files = self.param_files_input.text()
        exclude_scaled = self.exclude_combo.currentText()
        scaling_value = self.scaling_input.value()
        dielectric_constant = self.dielectric_input.value()
        cutoff = self.cutoff_input.value()
        pairlist_distance = self.pairlist_distance_input.value()
        margin = self.margin_input.value()
        stepspercycle = self.stepspercycle_input.value()
        rigid_bonds = self.rigidbonds_combo.currentText()
        rigid_tolerance = self.rigid_tolerance_input.value()
        rigid_iterations = self.rigid_iterations_input.value()
        pme_enabled = self.pme_on_radio.isChecked()
        langevindynamics = self.langevindynamics_combo.currentText()
        langevindamping = self.langevin_damping_input.value()
        langevintemp = self.langevintemp_input.value()
        langevinhydrogen = self.langevinhydrogen_combo.currentText()
        usegroup_pressure = self.usegroup_pressure_combo.currentText()
        useflexiblecell = self.useflexiblecell_combo.currentText()
        useconstantarea = self.useconstantarea_combo.currentText()
        langevinpiston = self.langevinpiston_combo.currentText()
        langevinpistontarget = self.langevinpistontarget_input.value()
        langevinpistonperiod = self.langevinpistonperiod_input.value()
        langevinpistondecay = self.langevinpistondecay_input.value()
        langevinpistontemp = self.langevinpistontemp_input.value()
        pme_tolerance = self.pme_tolerance_input.value()
        pme_grid_x = self.pme_grid_x_input.value()
        pme_grid_y = self.pme_grid_y_input.value()
        pme_grid_z = self.pme_grid_z_input.value()
        timestep = self.timestep_input.value()
        fullelectfreq = self.fullelectfreq_input.value()
        output_energies = self.output_energies_input.value()
        output_timing = self.output_timing_input.value()
        binary_output = self.binary_output_combo.currentText()
        output_name = self.output_name_input.text()
        restart_name = self.restart_name_input.text()
        restart_freq = self.restart_freq_input.value()
        binary_restart = self.binary_restart_combo.currentText()
        dcd_file = self.dcd_file_input.text()
        dcd_freq = self.dcd_freq_input.value()
        seed = self.seed_input.value()
        num_steps = self.num_steps_input.value()
        vector1_1 = self.vector1_x_input.value()
        vector1_2 = self.vector1_y_input.value()
        vector1_3 = self.vector1_z_input.value()
        vector2_1 = self.vector2_x_input.value()
        vector2_2 = self.vector2_y_input.value()
        vector2_3 = self.vector2_z_input.value()
        vector3_1 = self.vector3_x_input.value()
        vector3_2 = self.vector3_y_input.value()
        vector3_3 = self.vector3_z_input.value()
        cell_origin_x = self.cell_origin_x_input.value()
        cell_origin_y = self.cell_origin_y_input.value()
        cell_origin_z = self.cell_origin_z_input.value()
        wrapping_water = self.wrapping_water_combo.currentText()
        extra_text = self.extra_input.toPlainText()


        if self.param_checkbox.isChecked() and not param_files:
            QMessageBox.warning(self, 'Error', 'Please upload parameter files or disable paratypecharm.')
            return False


        if self.switch_checkbox.isChecked():
            switch_distance = self.switch_distance_input.value()
        else:
            switch_distance = None

        result = self.saveToFile(psf_file, coor_file, vel_file, extsystem_file, param_files, exclude_scaled, scaling_value, dielectric_constant, switch_distance, cutoff,
                        pairlist_distance, margin, stepspercycle, rigid_bonds,
                        rigid_tolerance, rigid_iterations, langevindynamics, langevindamping, langevinhydrogen, langevintemp, usegroup_pressure,
                        useconstantarea, useflexiblecell, langevinpiston, langevinpistonperiod, langevinpistondecay, langevinpistontarget, langevinpistontemp,
                        pme_enabled, pme_tolerance, pme_grid_x, pme_grid_y,
                        pme_grid_z, output_energies, timestep, fullelectfreq, output_timing, binary_output,
                        output_name, restart_name, restart_freq, binary_restart, dcd_file, dcd_freq, seed,
                        num_steps,
                        vector1_1, vector1_2, vector1_3, vector2_1,
                        vector2_2, vector2_3, vector3_1, vector3_2, vector3_3, cell_origin_x, cell_origin_y,
                        cell_origin_z, wrapping_water, extra_text)

        if result:
            print('Your simulation parameters are saved to configuration file.')
            QMessageBox.information(self, 'Success', 'Your simulation parameters are saved to configuration file.')
        return result

    def saveToFile(self, psf_file, coor_file, vel_file, extsystem_file, param_files, exclude_scaled, scaling_value, dielectric_constant, switch_distance, cutoff,
                   pairlist_distance, margin, stepspercycle, rigid_bonds,
                   rigid_tolerance, rigid_iterations, langevindynamics, langevindamping, langevinhydrogen, langevintemp, usegroup_pressure,
                   useconstantarea, useflexiblecell, langevinpiston, langevinpistonperiod, langevinpistondecay, langevinpistontarget,
                   langevinpistontemp, pme_enabled, pme_tolerance, pme_grid_x, pme_grid_y, pme_grid_z,
                   output_energies, timestep, fullelectfreq, output_timing, binary_output,
                   output_name, restart_name, restart_freq, binary_restart, dcd_file, dcd_freq, seed, num_steps, vector1_1, vector1_2, vector1_3, vector2_1, vector2_2,
                   vector2_3, vector3_1, vector3_2, vector3_3, cell_origin_x, cell_origin_y, cell_origin_z,
                   wrapping_water, extra_text):

        
        default_name = 'production.conf'
        if hasattr(self, 'directory_setup_tab') and self.directory_setup_tab:
            save_dir = self.directory_setup_tab.get_directory()
            if save_dir:
                default_path = os.path.join(save_dir, default_name)
            else:
                default_path = default_name
        else:
            default_path = default_name

        file_name_prd, selected_filter = QFileDialog.getSaveFileName(self, 'Save Configuration File', default_path, 'All Files (*);;Config Files/Inp Files (*.conf *.inp)')
        if not file_name_prd:
            return False
        
        if '.' not in file_name_prd:
            if 'conf' in selected_filter:
                file_name_prd += '.conf'
            elif 'inp' in selected_filter:
                file_name_prd += '.inp'
            else:
                file_name_prd += '.conf'

        with open(file_name_prd, 'w') as file:
            file.write("##############################################\n")
            file.write("#### input topology and initial structure ####\n")
            file.write("##############################################\n")
            file.write(f'structure           {psf_file}\n')
            file.write(f'coordinates         {coor_file}\n')
            file.write(f'velocities          {vel_file}\n')
            file.write(f'extendedsystem      {extsystem_file}\n\n\n')

            file.write("##############################################\n")
            file.write("#### force field block ####\n")
            file.write("##############################################\n")
            file.write(f'paratypecharmm         on\n')
            for param_files in self.selected_param_files:
                file.write(f'parameters        {os.path.basename(param_files)}\n')
            file.write(f'exclude                {exclude_scaled}\n\n\n')
            file.write(f'1-4scaling            {scaling_value}\n')
            file.write(f'dielectric             {dielectric_constant}\n')


            file.write("##############################################\n")
            file.write("#### dealing with long-range interactions ####\n")
            file.write("##############################################\n")
            file.write(f'switching               on \n\n\n')
            file.write(f'switchdist              {switch_distance}\n')
            file.write(f'cutoff                  {cutoff}\n')
            file.write(f'pairlistdist            {pairlist_distance}\n')
            file.write(f'margin                  {margin}\n')
            file.write(f'stepspercycle           {stepspercycle}\n')
            file.write(f'rigidBonds              {rigid_bonds}\n')
            file.write(f'rigidTolerance          {rigid_tolerance:.5f}\n')
            file.write(f'rigidIterations         {rigid_iterations}\n\n\n')


            file.write("##############################################\n")
            file.write("#### Constant Temperature Control ############\n")
            file.write("##############################################\n")
            file.write(f'langevin                {langevindynamics}\n')
            file.write(f'langevinDamping         {langevindamping}\n')
            file.write(f'langevinTemp            {langevintemp}\n')
            file.write(f'langevinHydrogen        {langevinhydrogen}\n\n\n')


            file.write("##############################################\n")
            file.write("#### Constant Pressure Control ###############\n")
            file.write("##############################################\n")            
            file.write(f'useGroupPressure             {usegroup_pressure}\n')
            file.write(f'useFlexibleCell              {useflexiblecell}\n')
            file.write(f'useConstantArea              {useconstantarea}\n')
            file.write(f'langevinPiston               {langevinpiston}\n')
            file.write(f'langevinPistonTarget         {langevinpistontarget:.6f}\n')
            file.write(f'langevinPistonPeriod         {langevinpistonperiod}\n')
            file.write(f'langevinPistonDecay          {langevinpistondecay}\n')
            file.write(f'langevinPistonTemp           {langevinpistontemp}\n')


            file.write("##############################################\n")
            file.write("#### Ewald electrostatics ####################\n")
            file.write("##############################################\n")
            file.write(f'PME                 {"on" if pme_enabled else "off"}\n')
            file.write(f'PMETolerance        {pme_tolerance:.6f}\n')
            file.write(f'PMEGridSizeX        {pme_grid_x}\n')
            file.write(f'PMEGridSizeY        {pme_grid_y}\n')
            file.write(f'PMEGridSizeZ        {pme_grid_z}\n\n\n')


            file.write("##############################################\n")
            file.write("#### parameters for integrator and MTS #######\n")
            file.write("##############################################\n")
            file.write(f'timestep                  {timestep}\n')
            file.write(f'fullElectFrequency        {fullelectfreq}\n\n\n')


            file.write("##############################################\n")
            file.write("#### the output ##############################\n")
            file.write("##############################################\n")            
            file.write(f'outputenergies           {output_energies}\n')
            file.write(f'outputtiming             {output_timing}\n')
            file.write(f'binaryoutput             {binary_output}\n')
            file.write(f'outputname               {output_name}\n')
            file.write(f'restartname              {restart_name}\n')
            file.write(f'restartfreq              {restart_freq}\n')
            file.write(f'binaryrestart            {binary_restart}\n')
            file.write(f'DCDfile                  {dcd_file}\n')
            file.write(f'dcdfreq                  {dcd_freq}\n\n\n')
            if extra_text:
                file.write(f'{extra_text}\n')

            file.write("##############################################\n")
            file.write("#### MD protocol block #######################\n")
            file.write("##############################################\n")
            file.write(f'seed              {seed}\n')
            file.write(f'numsteps          {num_steps}\n\n')
            
            file.write("##############################################\n")
            file.write("#### periodic boundary conditions ############\n")
            file.write("##############################################\n")
            file.write(f'cellBasisVector1           {vector1_1} {vector1_2} {vector1_3}\n')
            file.write(f'cellBasisVector2           {vector2_1} {vector2_2} {vector2_3}\n')
            file.write(f'cellBasisVector3           {vector3_1} {vector3_2} {vector3_3}\n')
            file.write(f'cellOrigin                 {cell_origin_x} {cell_origin_y} {cell_origin_z}\n\n')
            file.write(f'wrapWater                  {wrapping_water}\n')
            
        return True

    def productionAction(self):
        result = self.submitForm()
        if result:
            print('Production file generated successfully.')
            QMessageBox.information(self, 'Production', 'Production file generated successfully.')



class CpuCoreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Check CPU Cores")
        self.setFixedSize(300, 150)

        
        cpu_cores = os.cpu_count()

        
        layout = QVBoxLayout()

        
        self.label = QLabel(f"Available CPU Cores: {cpu_cores}")
        layout.addWidget(self.label)

        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)


class DirectorySetupTab(QWidget):
    def __init__(self):
        super().__init__()
        self.directory = ""
        self.next_callback = None  
        
        layout = QVBoxLayout()
        
        self.dir_label = QLabel("Select Working Directory for Simulation Files:")
        self.dir_input = QLineEdit()
        self.dir_button = QPushButton("Browse")
        self.dir_button.clicked.connect(self.browse_directory)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_button)
        
        layout.addWidget(self.dir_label)
        layout.addLayout(dir_layout)
        
        
        self.next_button = QPushButton("Next")
        self.next_button.setFixedWidth(140)
        self.next_button.setMinimumHeight(40)
        self.next_button.setStyleSheet("margin-top: 16px; margin-bottom: 8px;")
        self.next_button.clicked.connect(self.on_next_clicked)
        layout.addWidget(self.next_button, alignment=Qt.AlignRight)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Working Directory")
        if directory:
            self.directory = directory
            self.dir_input.setText(directory)
            QMessageBox.information(self, "Directory Selected", f"Working directory set to:\n{directory}")
    
    def get_directory(self):
        if not self.directory:
            QMessageBox.warning(self, "Warning", "Please select a directory first!")
            return None
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        return self.directory

    def on_next_clicked(self):
        if self.next_callback:
            self.next_callback()


class RunTab(QWidget):
    def __init__(self):
        super().__init__()
        self.process = None
        self.directory_setup_tab = None  
        layout = QVBoxLayout()

        self.namd_version_combo = QComboBox()
        self.namd_version_combo.addItems(["2", "3"])
        self.namd_version_combo.setCurrentIndex(0)
        namd_version_layout = QHBoxLayout()
        namd_version_layout.addWidget(QLabel("Select NAMD Version:"))
        namd_version_layout.addWidget(self.namd_version_combo)

       
        self.cpu_cores_spinbox = QSpinBox()
        self.cpu_cores_spinbox.setRange(1, os.cpu_count())
        self.cpu_cores_spinbox.setValue(4)  
        cpu_cores_layout = QHBoxLayout()
        cpu_cores_layout.addWidget(QLabel("Number of CPU Cores:"))
        cpu_cores_layout.addWidget(self.cpu_cores_spinbox)

        
        self.check_cores_button = QPushButton("Check Available Cores")
        self.check_cores_button.clicked.connect(self.open_cpu_core_dialog)
        cpu_cores_layout.addWidget(self.check_cores_button)

        self.min_file_select_tab = QLineEdit(self)
        self.min_file_select_tab.setPlaceholderText("Select minimization file with .conf or .inp or .txt extension")
        self.min_file_select_button = QPushButton("Browse")
        self.min_file_select_button.clicked.connect(self.select_min_file)

        min_file_layout = QHBoxLayout()
        min_file_layout.addWidget(QLabel("Select Minimization Configuration file:"))
        min_file_layout.addWidget(self.min_file_select_tab)
        min_file_layout.addWidget(self.min_file_select_button)

        self.heat_file_select_tab = QLineEdit(self)
        self.heat_file_select_tab.setPlaceholderText("Select heating file with .conf or .inp or .txt extension")
        self.heat_file_select_button = QPushButton("Browse")
        self.heat_file_select_button.clicked.connect(self.select_heat_file)

        heat_file_layout = QHBoxLayout()
        heat_file_layout.addWidget(QLabel("Select Heating Configuration file:"))
        heat_file_layout.addWidget(self.heat_file_select_tab)
        heat_file_layout.addWidget(self.heat_file_select_button)

        self.equil_file_select_tab = QLineEdit(self)
        self.equil_file_select_tab.setPlaceholderText("Select equilibration file with .conf or .inp or .txt extension")
        self.equil_file_select_button = QPushButton("Browse")
        self.equil_file_select_button.clicked.connect(self.select_equil_file)

        equil_file_layout = QHBoxLayout()
        equil_file_layout.addWidget(QLabel("Select Equilibration Configuration file:"))
        equil_file_layout.addWidget(self.equil_file_select_tab)
        equil_file_layout.addWidget(self.equil_file_select_button)
        
        self.prod_file_select_tab = QLineEdit(self)
        self.prod_file_select_tab.setPlaceholderText("Select production file with .conf or .inp or .txt extension")
        self.prod_file_select_button = QPushButton("Browse")
        self.prod_file_select_button.clicked.connect(self.select_prod_file)

        prod_file_layout = QHBoxLayout()
        prod_file_layout.addWidget(QLabel("Select Production Configuration file:"))
        prod_file_layout.addWidget(self.prod_file_select_tab)
        prod_file_layout.addWidget(self.prod_file_select_button)
        
        
        self.run_button = QPushButton("Configure my Simulation")
        self.run_button.clicked.connect(self.run_simulations)

        
        layout.addLayout(namd_version_layout)
        layout.addLayout(cpu_cores_layout)
        layout.addLayout(min_file_layout)
        layout.addLayout(heat_file_layout)
        layout.addLayout(equil_file_layout)
        layout.addLayout(prod_file_layout)
        layout.addWidget(self.run_button)


        self.setLayout(layout)
    
    def select_min_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select input file", "", "Config Files (*.conf);;All Files (*)")
        if file_path:
            self.min_file_select_tab.setText(file_path)

    def select_heat_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select input file", "", "Config Files (*.conf);;All Files (*)")
        if file_path:
            self.heat_file_select_tab.setText(file_path)
    
    def select_equil_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select input file", "", "Config Files (*.conf);;All Files (*)")
        if file_path:
            self.equil_file_select_tab.setText(file_path)

    def select_prod_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select input file", "", "Config Files (*.conf);;All Files (*)")
        if file_path:
            self.prod_file_select_tab.setText(file_path)

    def open_cpu_core_dialog(self):
        """Opens the dialog to check available CPU cores."""
        dialog = CpuCoreDialog(self)
        dialog.exec()

    
    def run_simulations(self):
        def run_task():
            batch_file = None  
            try:
                
                selected_cores = self.cpu_cores_spinbox.value()
                selected_namd_version = self.namd_version_combo.currentText()
                namd_version = rf"C:\NAMD\namd{selected_namd_version}.exe"
                min_path = self.min_file_select_tab.text().strip()
                heat_path = self.heat_file_select_tab.text().strip()
                equil_path = self.equil_file_select_tab.text().strip()
                prod_path = self.prod_file_select_tab.text().strip()

                if not hasattr(self, 'directory_setup_tab') or not self.directory_setup_tab:
                    QMessageBox.warning(self, "Error", "Directory setup tab not initialized.")
                    return

                
                save_directory = self.directory_setup_tab.get_directory()

                if not save_directory:
                    QMessageBox.warning(self, "Error", "Please select a directory to save files.")
                    return

                
                batch_file = os.path.join(save_directory, "simulation.bat")

                
                batch_script = f"""@echo off
echo Current directory: %CD%

REM Run minimization
echo Running minimization...
"{namd_version}" +p{selected_cores} "{min_path}" > "{save_directory}/min.log"
if %errorlevel% neq 0 (
    echo Minimization failed.
    pause
    exit /b %errorlevel%
)

REM Run heating
echo Running heating...
"{namd_version}" +p{selected_cores} "{heat_path}" > "{save_directory}/heat.log"
if %errorlevel% neq 0 (
    echo Heating failed.
    pause
    exit /b %errorlevel%
)

REM Run equilibration
echo Running equilibration...
"{namd_version}" +p{selected_cores} "{equil_path}" > "{save_directory}/equil.log"
if %errorlevel% neq 0 (
    echo Equilibration failed.
    pause
    exit /b %errorlevel%
)

REM Run production
echo Running production...
"{namd_version}" +p{selected_cores} "{prod_path}" > "{save_directory}/prod.log"
if %errorlevel% neq 0 (
    echo Production failed.
    pause
    exit /b %errorlevel%
)

echo All simulations completed successfully.
pause
"""
                
                with open(batch_file, "w") as f:
                    f.write(batch_script)

                
                self.process = subprocess.Popen(batch_file, shell=True)
                self.process.wait()

                if self.process.returncode == 0:
                    self.worker.progress.emit(100)
                else:
                    raise Exception("Simulation run failed")

            except Exception as e:
                raise e

            finally:
                
                if batch_file and os.path.exists(batch_file):
                    try:
                        os.remove(batch_file)
                    except:
                        pass  

        
        self.worker = Worker(run_task)
        self.worker.finished.connect(self.on_simulation_finished)
        self.worker.error.connect(self.on_simulation_error)
        self.worker.start()

    def closeEvent(self, event):
        if self.process and self.process.poll() in None:
            self.process.terminate(event)
            self.process.wait()

    def on_simulation_finished(self):
        QMessageBox.information(self, "Success", "Simulations run successfully.")

    def on_simulation_error(self, error_message):
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.ico'))

        self.settings = QSettings("NAMD-Automator", "NAMD-Automator")  

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        self.welcome_page = self.setup_welcome_page()
        self.central_stack.addWidget(self.welcome_page)

        self.tab_widget = QTabWidget()
        self.central_stack.addWidget(self.tab_widget)
        
        
        self.directory_setup_tab = DirectorySetupTab()
        self.minimization_tab = QWidget()
        self.heating_tab = QWidget()
        self.equilibrium_tab = QWidget()
        self.product_tab = QWidget()
        self.run_tab = RunTab()
        self.help_tab = QWidget()

        
        self.tab_widget.addTab(self.directory_setup_tab, "Set Directory")
        self.tab_widget.addTab(self.minimization_tab, "Minimization")
        self.tab_widget.addTab(self.heating_tab, "Heating")
        self.tab_widget.addTab(self.equilibrium_tab, "Equilibration")
        self.tab_widget.addTab(self.product_tab, "Production")
        self.tab_widget.addTab(self.run_tab, "Manage Resources")
        self.tab_widget.addTab(self.help_tab, "Help")

        
        self.setup_minimization_tab()
        self.setup_heating_tab()
        self.setup_equilibrium_tab()
        self.setup_product_tab()
        self.setup_help_tab()

        
        self.minimization_form.directory_setup_tab = self.directory_setup_tab
        self.heating_form.directory_setup_tab = self.directory_setup_tab
        self.equilibrium_form.directory_setup_tab = self.directory_setup_tab
        self.production_form.directory_setup_tab = self.directory_setup_tab
        self.run_tab.directory_setup_tab = self.directory_setup_tab

        
        self.minimization_form.heating_form = self.heating_form
        self.minimization_form.equilibrium_form = self.equilibrium_form
        self.minimization_form.production_form = self.production_form

        
        self.directory_setup_tab.next_callback = self.go_to_next_tab

        self.setWindowTitle("NAMD Automator")
        self.resize(800, 500)
        self.central_stack.setCurrentWidget(self.welcome_page)



    def setup_welcome_page(self):
        """Set up the welcome page."""
        welcome_widget = QWidget()
        layout = QVBoxLayout()

        welcome_label = QLabel("<h1>Welcome to NAMD Automator</h1>")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        description_label = QLabel(
        "<div style='text-align: center;'>"
        "<p>This tool helps you automate NAMD simulations for molecular dynamics.</p>"
        "<p>Use the tabs to configure Minimization, Heating, Equilibration, and Production and manage resources to ease simulation.</p>"
        "</div>"
        )
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        
        copyright_label = QLabel(
        "<div style='text-align: center; font-size: 12px;'>"
        "© ROHAN MESHRAM LAB"
        "</div>"
        )
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)

        continue_button = QPushButton("Continue")
        continue_button.clicked.connect(self.show_main_tabs)
        layout.addWidget(continue_button)

        welcome_widget.setLayout(layout)
        return welcome_widget
    

    def show_main_tabs(self):
        self.settings.setValue("welcome_shown", True)
        self.central_stack.setCurrentWidget(self.tab_widget)

        
    def setup_minimization_tab(self):
        layout = QVBoxLayout()

        container_widget = QWidget()
        container_layout = QVBoxLayout()

        checkbox_layout = QHBoxLayout()
        self.use_same = QCheckBox('Use same value of the parameters in the next tabs', self)
        self.use_same.stateChanged.connect(self.copyAllValues)
        checkbox_layout.addWidget(self.use_same)

        self.minimization_form = MinimizationGUI() 
        container_layout.addWidget(self.minimization_form)
        container_layout.addLayout(checkbox_layout)

        self.next_button = QPushButton("Next", self)
        self.next_button.setFixedWidth(140)
        self.next_button.setMinimumHeight(40)
        self.next_button.setStyleSheet("margin-top: 16px; margin-bottom: 8px;")
        self.next_button.clicked.connect(self.go_to_next_tab)
        container_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        container_widget.setLayout(container_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container_widget)

        layout.addWidget(scroll_area)
        self.minimization_tab.setLayout(layout)

    def setup_heating_tab(self):
            layout = QVBoxLayout()

            container_widget = QWidget()
            container_layout = QVBoxLayout()

            self.heating_form = HeatingGUI()  
            container_layout.addWidget(self.heating_form)

            self.next_button = QPushButton("Next", self)
            self.next_button.setFixedWidth(140)
            self.next_button.setMinimumHeight(40)
            self.next_button.setStyleSheet("margin-top: 16px; margin-bottom: 8px;")
            self.next_button.clicked.connect(self.go_to_next_tab)
            container_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

            container_widget.setLayout(container_layout)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(container_widget)

            layout.addWidget(scroll_area)
            self.heating_tab.setLayout(layout)

    def setup_equilibrium_tab(self):
            layout = QVBoxLayout()

            container_widget = QWidget()
            container_layout = QVBoxLayout()

            self.equilibrium_form = EquilibriumGUI()
            container_layout.addWidget(self.equilibrium_form)

            self.next_button = QPushButton("Next", self)
            self.next_button.setFixedWidth(140)
            self.next_button.setMinimumHeight(40)
            self.next_button.setStyleSheet("margin-top: 16px; margin-bottom: 8px;")
            self.next_button.clicked.connect(self.go_to_next_tab)
            container_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

            container_widget.setLayout(container_layout)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(container_widget)

            layout.addWidget(scroll_area)
            self.equilibrium_tab.setLayout(layout)

    def setup_product_tab(self):
            layout = QVBoxLayout()

            container_widget = QWidget()
            container_layout = QVBoxLayout()

            self.production_form = ProductionGUI() 
            container_layout.addWidget(self.production_form)

            self.next_button = QPushButton("Next", self)
            self.next_button.setFixedWidth(140)
            self.next_button.setMinimumHeight(40)
            self.next_button.setStyleSheet("margin-top: 16px; margin-bottom: 8px;")
            self.next_button.clicked.connect(self.go_to_next_tab)
            container_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

            container_widget.setLayout(container_layout)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(container_widget)

            layout.addWidget(scroll_area)
            self.product_tab.setLayout(layout)





    def copyAllValues(self, state):
        if state == Qt.Checked:
           
            min_form = self.minimization_form
            heat_form = self.heating_form
            equil_form = self.equilibrium_form
            prod_form = self.production_form

            
            heat_form.heat_exclude_combo.setCurrentText(min_form.min_exclude_combo.currentText())
            equil_form.equil_exclude_combo.setCurrentText(min_form.min_exclude_combo.currentText())
            prod_form.exclude_combo.setCurrentText(min_form.min_exclude_combo.currentText())

            
            heat_form.heat_scaling_input.setValue(min_form.min_scaling_input.value())
            equil_form.equil_scaling_input.setValue(min_form.min_scaling_input.value())
            prod_form.scaling_input.setValue(min_form.min_scaling_input.value())

            
            heat_form.heat_dielectric_input.setValue(min_form.min_dielectric_input.value())
            equil_form.equil_dielectric_input.setValue(min_form.min_dielectric_input.value())
            prod_form.dielectric_input.setValue(min_form.min_dielectric_input.value())

            
            heat_form.heat_switch_distance_input.setValue(min_form.min_switch_distance_input.value())
            equil_form.equil_switch_distance_input.setValue(min_form.min_switch_distance_input.value())
            prod_form.switch_distance_input.setValue(min_form.min_switch_distance_input.value())

           
            heat_form.heat_cutoff_input.setValue(min_form.min_cutoff_input.value())
            equil_form.equil_cutoff_input.setValue(min_form.min_cutoff_input.value())
            prod_form.cutoff_input.setValue(min_form.min_cutoff_input.value())

           
            heat_form.heat_pairlist_distance_input.setValue(min_form.min_pairlist_distance_input.value())
            equil_form.equil_pairlist_distance_input.setValue(min_form.min_pairlist_distance_input.value())
            prod_form.pairlist_distance_input.setValue(min_form.min_pairlist_distance_input.value())

            
            heat_form.heat_margin_input.setValue(min_form.min_margin_input.value())
            equil_form.equil_margin_input.setValue(min_form.min_margin_input.value())
            prod_form.margin_input.setValue(min_form.min_margin_input.value())

            
            heat_form.heat_stepspercycle_input.setValue(min_form.min_stepspercycle_input.value())
            equil_form.equil_stepspercycle_input.setValue(min_form.min_stepspercycle_input.value())
            prod_form.stepspercycle_input.setValue(min_form.min_stepspercycle_input.value())

            
            heat_form.heat_rigidbonds_combo.setCurrentText(min_form.min_rigidbonds_combo.currentText())
            equil_form.equil_rigidbonds_combo.setCurrentText(min_form.min_rigidbonds_combo.currentText())
            prod_form.rigidbonds_combo.setCurrentText(min_form.min_rigidbonds_combo.currentText())

            
            heat_form.heat_rigid_tolerance_input.setValue(min_form.min_rigid_tolerance_input.value())
            equil_form.equil_rigid_tolerance_input.setValue(min_form.min_rigid_tolerance_input.value())
            prod_form.rigid_tolerance_input.setValue(min_form.min_rigid_tolerance_input.value())


            heat_form.heat_rigid_iterations_input.setValue(min_form.min_rigid_iterations_input.value())
            equil_form.equil_rigid_iterations_input.setValue(min_form.min_rigid_iterations_input.value())
            prod_form.rigid_iterations_input.setValue(min_form.min_rigid_iterations_input.value())

            
            heat_form.heat_pme_tolerance_input.setValue(min_form.min_pme_tolerance_input.value())
            equil_form.equil_pme_tolerance_input.setValue(min_form.min_pme_tolerance_input.value())
            prod_form.pme_tolerance_input.setValue(min_form.min_pme_tolerance_input.value())

            
            heat_form.heat_pme_grid_x_input.setValue(min_form.min_pme_grid_x_input.value())
            heat_form.heat_pme_grid_y_input.setValue(min_form.min_pme_grid_y_input.value())
            heat_form.heat_pme_grid_z_input.setValue(min_form.min_pme_grid_z_input.value())
            equil_form.equil_pme_grid_x_input.setValue(min_form.min_pme_grid_x_input.value())
            equil_form.equil_pme_grid_y_input.setValue(min_form.min_pme_grid_y_input.value())
            equil_form.equil_pme_grid_z_input.setValue(min_form.min_pme_grid_z_input.value())
            prod_form.pme_grid_x_input.setValue(min_form.min_pme_grid_x_input.value())
            prod_form.pme_grid_y_input.setValue(min_form.min_pme_grid_y_input.value())
            prod_form.pme_grid_z_input.setValue(min_form.min_pme_grid_z_input.value())

            
            heat_form.heat_binary_restart_combo.setCurrentText(min_form.min_binary_restart_combo.currentText())
            equil_form.equil_binary_restart_combo.setCurrentText(min_form.min_binary_restart_combo.currentText())
            prod_form.binary_restart_combo.setCurrentText(min_form.min_binary_restart_combo.currentText())

            
            heat_form.heat_vector1_x_input.setValue(min_form.min_vector1_x_input.value())
            heat_form.heat_vector1_y_input.setValue(min_form.min_vector1_y_input.value())
            heat_form.heat_vector1_z_input.setValue(min_form.min_vector1_z_input.value())
            equil_form.equil_vector1_x_input.setValue(min_form.min_vector1_x_input.value())
            equil_form.equil_vector1_y_input.setValue(min_form.min_vector1_y_input.value())
            equil_form.equil_vector1_z_input.setValue(min_form.min_vector1_z_input.value())
            prod_form.vector1_x_input.setValue(min_form.min_vector1_x_input.value())
            prod_form.vector1_y_input.setValue(min_form.min_vector1_y_input.value())
            prod_form.vector1_z_input.setValue(min_form.min_vector1_z_input.value())

            heat_form.heat_vector2_x_input.setValue(min_form.min_vector2_x_input.value())
            heat_form.heat_vector2_y_input.setValue(min_form.min_vector2_y_input.value())
            heat_form.heat_vector2_z_input.setValue(min_form.min_vector2_z_input.value())
            equil_form.equil_vector2_x_input.setValue(min_form.min_vector2_x_input.value())
            equil_form.equil_vector2_y_input.setValue(min_form.min_vector2_y_input.value())
            equil_form.equil_vector2_z_input.setValue(min_form.min_vector2_z_input.value())
            prod_form.vector2_x_input.setValue(min_form.min_vector2_x_input.value())
            prod_form.vector2_y_input.setValue(min_form.min_vector2_y_input.value())
            prod_form.vector2_z_input.setValue(min_form.min_vector2_z_input.value())

            heat_form.heat_vector3_x_input.setValue(min_form.min_vector3_x_input.value())
            heat_form.heat_vector3_y_input.setValue(min_form.min_vector3_y_input.value())
            heat_form.heat_vector3_z_input.setValue(min_form.min_vector3_z_input.value())
            equil_form.equil_vector3_x_input.setValue(min_form.min_vector3_x_input.value())
            equil_form.equil_vector3_y_input.setValue(min_form.min_vector3_y_input.value())
            equil_form.equil_vector3_z_input.setValue(min_form.min_vector3_z_input.value())
            prod_form.vector3_x_input.setValue(min_form.min_vector3_x_input.value())
            prod_form.vector3_y_input.setValue(min_form.min_vector3_y_input.value())
            prod_form.vector3_z_input.setValue(min_form.min_vector3_z_input.value())
            

            heat_form.heat_cell_origin_x_input.setValue(min_form.min_cell_origin_x_input.value())
            heat_form.heat_cell_origin_y_input.setValue(min_form.min_cell_origin_y_input.value()) 
            heat_form.heat_cell_origin_z_input.setValue(min_form.min_cell_origin_z_input.value())
            equil_form.equil_cell_origin_x_input.setValue(min_form.min_cell_origin_x_input.value())
            equil_form.equil_cell_origin_y_input.setValue(min_form.min_cell_origin_y_input.value())
            equil_form.equil_cell_origin_z_input.setValue(min_form.min_cell_origin_z_input.value())
            prod_form.cell_origin_x_input.setValue(min_form.min_cell_origin_x_input.value())
            prod_form.cell_origin_y_input.setValue(min_form.min_cell_origin_y_input.value())
            prod_form.cell_origin_z_input.setValue(min_form.min_cell_origin_z_input.value())  

            # Set 'Enable Switching' checkbox in subsequent tabs if checked in minimization
            if min_form.min_switch_checkbox.isChecked():
                heat_form.heat_switch_checkbox.setChecked(True)
                equil_form.equil_switch_checkbox.setChecked(True)
                prod_form.switch_checkbox.setChecked(True)



    def setup_help_tab(self):
        layout = QVBoxLayout()

        logo = QLabel()
        logo_path = get_resource_path("Savitribai_Phule_Pune_University_Logo.png")
        pixmap = QPixmap(logo_path)
        if not pixmap or pixmap.isNull():
            logo.setText("Logo not found")
        else:
            scaled_pixmap = pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(scaled_pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)


        
        help_text = """
        <h2>NAMD Automator</h2>
        <p><b>Version 1.0 (Beta)</b></p>

        <p><b>Bioinformatics Centre, Savitribai Phule Pune University, Pune, Maharashtra-411007, India</b></p>
        <p>&copy; ROHAN MESHRAM LAB</p>

        <h3>Video Tutorial</h3>
        <p>Watch the tutorial here: 
        <a href='https://www.youtube.com/playlist?list=PLFdE2bf3lv9y7v7bjj8tEhQxzBj31KU8f'>Video Tutorial</a></p>
        
        <h3> To contact the development team:</h3>
        <ul>
            <li>Mr. Manojit Mazumder (jeet2002.19@gmail.com)</li>
            <li>Dr. Rohan J Meshram (rohan_meshram@rediffmail.com)</li>
        </ul>

        <h3> Product Link </h3>
        <p> Check out the product over here:
        <a href='https://sourceforge.net/projects/namd-automator/'>SourceForge</a></p>
        """

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)  
        self.text_browser.setHtml(help_text)  
        layout.addWidget(self.text_browser)

        self.help_tab.setLayout(layout)

    def go_to_next_tab(self):
            current_index = self.tab_widget.currentIndex()
            if current_index < self.tab_widget.count() - 1:
                self.tab_widget.setCurrentIndex(current_index + 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())

