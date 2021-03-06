import argparse
import datetime
import math
import os

import matplotlib.pyplot as plt

from fpdf import FPDF

labels = {
    "clinical.sui": "subject unique identifier",
    "clinical.timestamp": "sit timestamp (days after first sit)",
    "clinical.duration": "sit duration (s)",
    "clinical.hr": "HR (bpm)",
    "clinical.hrv": "HRV (ms)",
    "clinical.qtc": "QTc (ms)",
    "clinical.qrs": "QRS (ms)",
    "clinical.spo2": "SpO2 (%)",
    "clinical.dbp": "diastolic BP (mmHg)",
    "clinical.sbp": "systolic BP (mmHg)",
    "clinical.pwv": "PWV (m/s)",
    "clinical.sv": "SV (mL)",
    "clinical.co": "CO (L/min)",
    "clinical.cardiac_index": "cardiac index (L/min/m^2)",
    "clinical.sv_index": "stroke volume index (mL/m^2)",
    "clinical.ptt": "PTT (ms)",
    "clinical.pat": "PAT (ms)",
    "clinical.seat_weight": "seated weight (lb)",
    "clinical.r_peak_loc": "R-peak locations (ms)",
    "clinical.respiration_rate": "respiration rate (breaths/min)",
    "clinical.ecg_elec_imped": "ECG electrode impedance (ohms)",
    "low_level.ppg_ir_dc": "PPG IR DC amplitude (pA)",
    "low_level.ppg_ir_pulsatile": "PPG IR pulsatile amplitude (pA)",
    "low_level.ppg_red_dc": "PPG red DC amplitude (pA)",
    "low_level.ppg_red_pulsatile": "PPG red pulsatile amplitude (pA)",
    "low_level.bcg_rms": "BCG emsemble RMS (N)",
    "ecg.q_amp": "Q-wave amplitude (uV)",
    "ecg.q_loc": "Q-wave location (ms)",
    "ecg.r_amp": "R-wave amplitude (uV)",
    "ecg.r_loc": "R-wave location (ms)",
    "ecg.s_amp": "S-wave amplitude (uV)",
    "ecg.s_loc": "S-wave location (ms)",
    "ecg.t_peak_amp": "T-wave peak amplitude (uV)",
    "ecg.t_peak_loc": "T-wave peak location (ms)",
    "ecg.t_end_amp": "T-wave end amplitude (uV)",
    "ecg.t_end_loc": "T-wave end location (ms)",
    "bcg.h_amp": "H-wave amplitude (N)",
    "bcg.h_loc": "H-wave location (ms)",
    "bcg.i_amp": "I-wave amplitude (N)",
    "bcg.i_loc": "I-wave location (ms)",
    "bcg.j_amp": "J-wave amplitude (N)",
    "bcg.j_loc": "J-wave location (ms)",
    "ppg.ir_min_tan_amp": "IR min tangent amplitude (pA)",
    "ppg.ir_min_tan_loc": "IR min tangent location (ms)",
    "ppg.ir_peak_amp": "IR peak amplitude (pA)",
    "ppg.ir_peak_loc": "IR peak location (ms)",
    "ppg.red_min_tan_amp": "red min tangent amplitude (pA)",
    "ppg.red_min_tan_loc": "red min tangent location (ms)",
    "ppg.red_peak_amp": "red peak amplitude (pA)",
    "ppg.red_peak_loc": "red peak location (ms)",
    "channel_format": "Channel Format",
}


class SeatReader:
    """
    A class that contains logic for reading the .csv files and creating a graph.
    """
    def __init__(self):
        """
        Initialize attributes and call high-level methods.
        """

        """
        The name of the input file.
        """
        self.filename = None

        """
        The list of unique SUI's in the input file, found using the 'clinical.sui' column.
        """
        self.sui_list = []
        """
        The earliest date for each SUI. Used to adjust x-axis to be relative instead of absolute, 
        if clinical.timestamp is the independent variable.
        """
        self.sui_starts = {}
        """
        The SUI's that the user wants to graph.
        """
        self.user_sui_list = []
        """
        The common prefix among every SUI. The user may omit the prefix to save typing.
        """
        self.sui_prefix = None

        """
        The list of variables available.
        """
        self.vars = []
        """
        The list of variables to graph.
        """
        self.graph_vars = []
        """
        The variable to graph on the horizontal axis.
        """
        self.independent_var = None
        """
        The name of the variable that is unique for each SUI, usually clinical.sui.
        """
        self.identifying_var = None

        """
        When true, the program will crash instead of asking for input via stdin.
        """
        self.no_input = False
        """
        When true, the program will show missing data as red lines.
        """
        self.show_missing = False
        """
        If not None, specifies the name of the PDF where the images should be saved
        """
        self.save_pdf = None

        """
        The list of data points for each variable for each SUI.
        """
        self.xAxis = {}
        self.yAxis = {}
        self.std = {}
        """
        The list of x values where the corresponding y value is missing
        """
        self.missing_data = {}

        self.get_args()
        self.get_vars()
        self.get_sui_list()
        self.check_args()
        self.get_data()
        self.condense_data()
        self.show_graph()

    def interpret_var(self, val, var_type):
        """
        Most variables should be interpreted as floats, but timestamps should be converted to datetime objects.
        :param val: The value to convert
        :param var_type: The name of the column
        :return: The value converted to the appropriate type
        """
        if var_type == "clinical.timestamp":
            return datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
        elif var_type == "clinical.sui":
            return val
        else:
            return float(val)

    def get_sui_list(self):
        """
        Get the list of unique SUI's from the input file, along with the earliest recorded date for each.
        :return: None; results are stored in self.sui_list and self.sui_starts
        """
        self.sui_list = []
        self.sui_starts = {}
        with open(self.filename, 'r') as f:
            for line_str in f:
                line = line_str.split(',')
                if line[0] == "clinical.sui":
                    continue
                sui = line[self.vars.index(self.identifying_var)]
                date = self.interpret_var(line[self.vars.index(self.independent_var)], self.independent_var)
                if sui not in self.sui_list and sui != "clinical.sui":
                    self.sui_list.append(sui)
                    self.sui_starts[sui] = date
                self.sui_starts[sui] = min(self.sui_starts[sui], date)

        if len(self.sui_list) == 0:
            print("No SUI's found in input file. Check that it is the expected format.")

        self.sui_prefix = self.sui_list[0]
        for sui in self.sui_list:
            while sui[:len(self.sui_prefix)] != self.sui_prefix[:len(self.sui_prefix)]:
                self.sui_prefix = self.sui_prefix[:-1]
                if len(self.sui_prefix) == 0:
                    break

    def get_vars(self):
        """
        Get the list of variables from the input file.
        :return: None; results are stored in self.vars
        """
        self.vars = []
        # get the list of variables from the first line of the input csv file
        with open(self.filename, 'r') as f:
            for line in f:
                self.vars = line.split(',')
                break

    def show_graph(self):
        """
        Create the graph and show it or save as images.
        :return: None
        """
        plt.figure()
        fig, ax = plt.subplots()
        images_paths = []
        for sui in self.user_sui_list:
            for var in self.graph_vars:
                var_name = var
                if var in labels:
                    var_name = labels[var]
                plt.bar(self.xAxis[sui][var], self.yAxis[sui][var], label=sui + " " + var_name,
                        yerr=self.std[sui][var], color='blue')
                plt.bar(self.xAxis[sui][var], self.missing_data[sui][var],
                        label=sui + " " + var_name + " percentage missing", color='red')
                if self.independent_var in labels:
                    plt.xlabel(labels[self.independent_var])
                else:
                    plt.xlabel(self.independent_var)
                plt.ylabel(var_name)
                plt.legend()
                if self.save_pdf is None:
                    plt.show()
                else:
                    plt.gca().legend().set_visible(False)
                    path = "temp_" + sui + "_" + var + ".png"
                    fig.set_size_inches(8, 10)
                    plt.savefig(path, dpi=100)
                    images_paths.append(path)
                    plt.clf()
        # create PDF
        if self.save_pdf is not None:
            pdf = FPDF()
            for sui in self.user_sui_list:
                for var in self.graph_vars:
                    var_name = var
                    if var in labels:
                        var_name = labels[var]
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 16)
                    pdf.image("temp_" + sui + "_" + var + ".png", 8, 30, 200, 250)
                    pdf.text(22, 35, sui + ": " + var_name)
                    os.remove("temp_" + sui + "_" + var + ".png")
            pdf.output(self.save_pdf)

    def get_args(self):
        """
        Get the command line arguments.
        :return: None; results are stored in self
        """
        parser = argparse.ArgumentParser(description='Parses a csv file from the seats experiment.')

        parser.add_argument("input_file", help="The input file to parse.")
        parser.add_argument("-s", "--sui", help="The SUI(s) to graph.", nargs='+')
        parser.add_argument("-v", "--vars", help="The variable(s) to graph.", nargs='+')
        parser.add_argument("-x", help="The variable to graph on the horizontal axis.", default="clinical.timestamp")
        parser.add_argument("-i", help="The variable that is unique for each user.", default="clinical.sui")
        parser.add_argument("-m", help="Show missing data as red lines.", type=bool, default=False)
        parser.add_argument("--no-input", help="If appropriate options are not specified, error out instead of "
                                               "asking for standard input.")
        parser.add_argument("--save", help="Saves the resulting graphs to the specified PDF")

        arguments = parser.parse_args()

        self.filename = arguments.input_file
        self.independent_var = arguments.x
        self.no_input = arguments.no_input
        self.identifying_var = arguments.i
        self.show_missing = arguments.m
        if arguments.sui:
            self.user_sui_list = arguments.sui
        if arguments.vars:
            self.graph_vars = arguments.vars

        self.user_sui_list = arguments.sui
        if not self.user_sui_list:
            self.user_sui_list = []

        if arguments.save:
            self.save_pdf = arguments.save

    def get_data(self):
        """
        Get the data from the input file.
        :return: None; results are stored in self.xAxis and self.yAxis
        """
        self.xAxis = {}
        self.yAxis = {}

        for sui in self.user_sui_list:
            self.xAxis[sui] = {}
            self.yAxis[sui] = {}
            self.missing_data[sui] = {}
            self.std[sui] = {}
            for var in self.graph_vars:
                self.xAxis[sui][var] = []
                self.yAxis[sui][var] = []
                self.missing_data[sui][var] = []
                self.std[sui][var] = []

        with open(self.filename, 'r') as f:
            for line in f:
                line = line.split(',')
                sui = line[0]
                if sui in self.user_sui_list:
                    x_val = self.interpret_var(line[self.vars.index(self.independent_var)], self.independent_var)
                    if self.independent_var == "clinical.timestamp":
                        x_val = (x_val - self.sui_starts[sui]).total_seconds() / (60 * 60 * 24)
                    for var in self.graph_vars:
                        if line[self.vars.index(var)] != '':
                            self.xAxis[sui][var].append(x_val)
                            self.yAxis[sui][var].append(self.interpret_var(line[self.vars.index(var)], var))
                        else:
                            self.missing_data[sui][var].append(x_val)

        for sui in self.user_sui_list:
            for var in self.graph_vars:
                self.xAxis[sui][var], self.yAxis[sui][var] = \
                    zip(*sorted(zip(self.xAxis[sui][var], self.yAxis[sui][var])))

    def check_args(self):
        """
        Ensure that the user entered valid arguments; ask for more if they are needed.
        :return: None; results are stored in self
        """
        if len(self.user_sui_list) == 0:
            print("No SUI(s) specified.")
            if self.no_input:
                exit(1)
            else:
                print("Enter SUI(s) to graph from the following options, separated by spaces:")
                for sui in self.sui_list:
                    print(sui)
                print("The common prefix '" + self.sui_prefix + "' was found. You may enter whole SUIs or just the "
                                                                "part after the common prefix.")
                while 1:
                    self.user_sui_list = input("\nEnter SUI(s) to graph, separated by spaces: ").split(' ')
                    if self.user_sui_list[0] == 'all':
                        self.user_sui_list = self.sui_list
                        break
                    for sui in self.user_sui_list:
                        if sui not in self.sui_list and self.sui_prefix + sui not in self.sui_list:
                            print("SUI " + sui + " not found in input file.")
                            # remove the sui from the list of sui's to graph
                            self.user_sui_list.remove(sui)
                    if len(self.user_sui_list) == 0:
                        print("No SUI(s) specified.")
                        continue
                    else:
                        break

        # add the prefix to any SUIs that are not in sui_list
        new_suis = []
        for sui in self.user_sui_list:
            if sui not in self.sui_list:
                new_suis.append(self.sui_prefix + sui)
            else:
                new_suis.append(sui)
        self.user_sui_list = new_suis

        # print the list of sui's to graph
        print("\nSUI(s) to graph:")
        for sui in self.user_sui_list:
            print(sui)

        # check if the variables were specified
        if self.graph_vars is not None:
            for var in self.graph_vars:
                if var not in self.vars:
                    print("Variable " + var + " not found in input file.")
                    self.graph_vars.remove(var)
        if self.graph_vars is None or len(self.graph_vars) == 0:
            print("No variable(s) specified.")
            if self.no_input:
                exit(1)
            else:
                print("Enter variable(s) to graph from the following options, separated by spaces:")
                for var in self.vars:
                    print(var)
                while 1:
                    self.graph_vars = input("\nEnter variable(s) to graph, separated by spaces: ").split(' ')
                    for var in self.graph_vars:
                        if var not in self.vars:
                            print("Variable " + var + " not found in input file.")
                            # remove the variable from the list of variables to graph
                            self.graph_vars.remove(var)
                    if len(self.graph_vars) == 0:
                        print("No variable(s) specified.")
                        continue
                    else:
                        break

        # print the list of variables to graph
        print("\nVariable(s) to graph:")
        for var in self.graph_vars:
            print(var)

        if self.independent_var not in self.vars:
            if self.no_input:
                exit(1)
            else:
                print("Enter the variable to graph on the horizontal axis from the following options:")
                for var in self.vars:
                    print(var)
                while 1:
                    self.independent_var = input("\nEnter the variable to graph on the horizontal axis: ")
                    if self.independent_var not in self.vars:
                        print("Variable " + self.independent_var + " not found in input file.")
                        continue
                    else:
                        break

        # print the variable to graph on the horizontal axis
        print("\nVariable to graph on the horizontal axis: " + self.independent_var)

        if self.user_sui_list is not None:
            new_sui_list = []
            for sui in self.user_sui_list:
                if sui == 'all':
                    new_sui_list = self.sui_list
                    break
                if sui not in self.sui_list and self.sui_prefix + sui not in self.sui_list:
                    print("SUI " + sui + " not found in input file.")
                new_sui_list.append(sui)
            self.user_sui_list = new_sui_list

    def condense_data(self):
        for sui in self.user_sui_list:
            for var in self.graph_vars:
                i = 0
                new_x_axis = []
                new_y_axis = []
                new_std = []
                new_missing_data = []

                while 1:
                    if i >= len(self.xAxis[sui][var]):
                        break

                    day = math.floor(self.xAxis[sui][var][i])
                    points = [self.yAxis[sui][var][i]]

                    i += 1
                    while i < len(self.xAxis[sui][var]) and day == math.floor(self.xAxis[sui][var][i]):
                        points.append(self.yAxis[sui][var][i])
                        i += 1

                    mean = sum(points) / len(points)
                    variance = sum([((x - mean) ** 2) for x in points]) / len(points)
                    res = variance ** 0.5

                    count_missing = 0
                    for missing_point in self.missing_data[sui][var]:
                        if day == math.floor(missing_point):
                            count_missing += 1
                    percentage_missing = count_missing / (count_missing + len(points))

                    new_x_axis.append(day)
                    new_y_axis.append(mean)
                    new_std.append(res)
                    new_missing_data.append(percentage_missing * mean)

                self.xAxis[sui][var] = new_x_axis
                self.yAxis[sui][var] = new_y_axis
                self.std[sui][var] = new_std
                self.missing_data[sui][var] = new_missing_data


if __name__ == '__main__':
    s = SeatReader()
