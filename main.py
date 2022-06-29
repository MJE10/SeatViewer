import argparse
import datetime
import os.path

import matplotlib.pyplot as plt


class SeatReader:
    def __init__(self):
        self.filename = None
        self.sui_list = []
        self.user_sui_list = []
        self.vars = []
        self.graph_vars = []
        self.independent_var = None
        self.no_input = False
        self.sui_prefix = None

    def get_sui_list(self):
        # get the list of sui's from the input csv file
        self.sui_list = []
        sui_starts = {}
        with open(self.filename, 'r') as f:
            for linex in f:
                line = linex.split(',')
                sui = line[0]
                if sui not in self.sui_list and sui != "clinical.sui":
                    self.sui_list.append(sui)
                    sui_starts[sui] = datetime.datetime.strptime(line[self.vars.index(self.independent_var)], "%Y-%m-%d %H:%M:%S")
                elif sui != "clinical.sui":
                    sui_starts[sui] = min(sui_starts[sui], datetime.datetime.strptime(line[self.vars.index(self.independent_var)],
                                                                                      "%Y-%m-%d %H:%M:%S"))

        if len(self.sui_list) == 0:
            print("No SUI's found in input file. Check that it is the expected format.")

        self.sui_prefix = self.sui_list[0]
        for sui in self.sui_list:
            while sui[:len(self.sui_prefix)] != self.sui_prefix[:len(self.sui_prefix)]:
                sui_prefix = self.sui_prefix[:-1]
                if len(sui_prefix) == 0:
                    break

    def get_vars(self):
        self.vars = []
        # get the list of variables from the first line of the input csv file
        with open(self.filename, 'r') as f:
            for line in f:
                self.vars = line.split(',')
                break

    def show_graph(self):
        plt.figure(figsize=(10, 10))
        for sui in user_suis:
            for var in user_vars:
                plt.plot(xAxis[sui][var], yAxis[sui][var], label=sui + " " + var)
                # plt.xticks(np.arange(0, len(xAxis[sui][var]), 30), rotation=90)

                # plt.yticks(np.arange(0, len(xAxis[sui]), 30))
        plt.xlabel(horizontal_var)
        if len(user_vars) == 1:
            plt.ylabel(user_vars[0])
        plt.legend()
        plt.show()

    def get_args(self):
        parser = argparse.ArgumentParser(description='Parses a csv file from the seats experiment.')

        parser.add_argument("input_file", help="The input file to parse.")
        parser.add_argument("-s", "--sui", help="The SUI(s) to graph.", nargs='+')
        parser.add_argument("-v", "--vars", help="The variable(s) to graph.", nargs='+')
        parser.add_argument("-x", help="The variable to graph on the horizontal axis.", default="clinical.timestamp")
        parser.add_argument("--no-input", help="If appropriate options are not specified, error out instead of "
                                               "asking for standard input.")

        arguments = parser.parse_args()

        self.filename = arguments.input_file
        self.independent_var = arguments.x
        self.no_input = arguments.no_input
        if arguments.sui:
            self.user_sui_list = arguments.sui
        if arguments.vars:
            self.graph_vars = arguments.vars

        # check if the sui's were specified
        self.user_sui_list = []
        if arguments.sui is not None:
            for sui in arguments.sui:
                if sui == 'all':
                    self.user_sui_list = self.sui_list
                    break
                if sui not in self.sui_list and self.sui_prefix + sui not in self.sui_list:
                    print("SUI " + sui + " not found in input file.")
                    arguments.sui.remove(sui)
                self.user_sui_list.append(sui)

    def get_data(self):
        xAxis = {}
        yAxis = {}

        for sui in user_suis:
            xAxis[sui] = {}
            yAxis[sui] = {}
            for var in user_vars:
                xAxis[sui][var] = []
                yAxis[sui][var] = []

        with open(args.input_file, 'r') as f:
            for line in f:
                line = line.split(',')
                if line[0] in user_suis:
                    for var in user_vars:
                        # insert the value so that the x axis is in order
                        index = 0
                        # while index < len(xAxis[line[0]][var]) and line[variables.index(horizontal_var)] < xAxis[line[0]][var][index]:
                        #     index += 1
                        if line[variables.index(var)] != '':
                            xAxis[line[0]][var].insert(index, ((datetime.datetime.strptime(
                                line[variables.index(horizontal_var)], "%Y-%m-%d %H:%M:%S") - sui_starts[
                                                                    line[0]]).total_seconds() / 1000) % (60 * 60 * 24))
                            yAxis[line[0]][var].insert(index, float(line[variables.index(var)]))
                        # else:
                        #     yAxis[line[0]][var].insert(index, 0)

        # reverse the lists
        for sui in user_suis:
            for var in user_vars:
                xAxis[sui][var].reverse()
                yAxis[sui][var].reverse()

    def check_args(self):
        if len(self.user_sui_list) == 0:
            print("No SUI(s) specified.")
            if self.no_input:
                exit(1)
            else:
                print("Enter SUI(s) to graph from the following options, separated by spaces:")
                for sui in self.sui_list:
                    print(sui)
                print("The common prefix '" + self.sui_prefix + "' was found. You may enter whole SUIs or just the part "
                                                           "after the common prefix.")
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
        for sui in user_suis:
            if sui not in sui_list:
                new_suis.append(sui_prefix + sui)
            else:
                new_suis.append(sui)
        user_suis = new_suis

        # print the list of sui's to graph
        print("\nSUI(s) to graph:")
        for sui in user_suis:
            print(sui)

        user_vars = []
        # check if the variables were specified
        if args.vars is not None:
            for var in args.vars:
                if var not in variables:
                    print("Variable " + var + " not found in input file.")
                    args.vars.remove(var)
        if args.vars is None or len(args.vars) == 0:
            print("No variable(s) specified.")
            if args.no_input:
                exit(1)
            else:
                print("Enter variable(s) to graph from the following options, separated by spaces:")
                for var in variables:
                    print(var)
                while 1:
                    user_vars = input("\nEnter variable(s) to graph, separated by spaces: ").split(' ')
                    for var in user_vars:
                        if var not in variables:
                            print("Variable " + var + " not found in input file.")
                            # remove the variable from the list of variables to graph
                            user_vars.remove(var)
                    if len(user_vars) == 0:
                        print("No variable(s) specified.")
                        continue
                    else:
                        break
        else:
            user_vars = args.vars

        # print the list of variables to graph
        print("\nVariable(s) to graph:")
        for var in user_vars:
            print(var)

        horizontal_var = args.x
        if horizontal_var not in variables:
            if args.no_input:
                exit(1)
            else:
                print("Enter the variable to graph on the horizontal axis from the following options:")
                for var in variables:
                    print(var)
                while 1:
                    horizontal_var = input("\nEnter the variable to graph on the horizontal axis: ")
                    if horizontal_var not in variables:
                        print("Variable " + horizontal_var + " not found in input file.")
                        continue
                    else:
                        break

        # print the variable to graph on the horizontal axis
        print("\nVariable to graph on the horizontal axis: " + horizontal_var)


# Initialize parser

# parser = argparse.ArgumentParser(description='Parses a csv file from the seats experiment.')
#
# parser.add_argument("input_file", help="The input file to parse.")
# parser.add_argument("-s", "--sui", help="The SUI(s) to graph.", nargs='+')
# parser.add_argument("-v", "--vars", help="The variable(s) to graph.", nargs='+')
# parser.add_argument("-x", help="The variable to graph on the horizontal axis.", default="clinical.timestamp")
# parser.add_argument("--no-input", help="If appropriate options are not specified, error out instead of "
#                                        "asking for standard input.")
#
# args = parser.parse_args()
#
# # check if the input file exists and is readable
# if not os.path.exists(args.input_file):
#     print("Input file does not exist.")
#     exit(1)
# if not os.access(args.input_file, os.R_OK):
#     print("Input file is not readable.")
#     exit(1)

# variables = []
# # get the list of variables from the first line of the input csv file
# with open(args.input_file, 'r') as f:
#     for line in f:
#         variables = line.split(',')
#         break

# get the list of sui's from the input csv file
# sui_list = []
# sui_starts = {}
# with open(args.input_file, 'r') as f:
#     for linex in f:
#         line = linex.split(',')
#         sui = line[0]
#         if sui not in sui_list and sui != "clinical.sui":
#             sui_list.append(sui)
#             sui_starts[sui] = datetime.datetime.strptime(line[variables.index(args.x)], "%Y-%m-%d %H:%M:%S")
#         elif sui != "clinical.sui":
#             sui_starts[sui] = min(sui_starts[sui], datetime.datetime.strptime(line[variables.index(args.x)], "%Y-%m-%d %H:%M:%S"))

# if len(sui_list) == 0:
#     print("No SUI's found in input file. Check that it is the expected format.")
#     exit(1)

# determine the length of the common prefix among all SUIs
# sui_prefix = sui_list[0]
# for sui in sui_list:
#     while sui[:len(sui_prefix)] != sui_prefix[:len(sui_prefix)]:
#         sui_prefix = sui_prefix[:-1]
#         if len(sui_prefix) == 0:
#             break

# # check if the sui's were specified
# user_suis = []
# if args.sui is not None:
#     for sui in args.sui:
#         if sui == 'all':
#             user_suis = sui_list
#             break
#         if sui not in sui_list and sui_prefix + sui not in sui_list:
#             print("SUI " + sui + " not found in input file.")
#             args.sui.remove(sui)
#         user_suis.append(sui)


# # add the prefix to any SUIs that are not in sui_list
# new_suis = []
# for sui in user_suis:
#     if sui not in sui_list:
#         new_suis.append(sui_prefix + sui)
#     else:
#         new_suis.append(sui)
# user_suis = new_suis
#
# # print the list of sui's to graph
# print("\nSUI(s) to graph:")
# for sui in user_suis:
#     print(sui)

# user_vars = []
# # check if the variables were specified
# if args.vars is not None:
#     for var in args.vars:
#         if var not in variables:
#             print("Variable " + var + " not found in input file.")
#             args.vars.remove(var)
# if args.vars is None or len(args.vars) == 0:
#     print("No variable(s) specified.")
#     if args.no_input:
#         exit(1)
#     else:
#         print("Enter variable(s) to graph from the following options, separated by spaces:")
#         for var in variables:
#             print(var)
#         while 1:
#             user_vars = input("\nEnter variable(s) to graph, separated by spaces: ").split(' ')
#             for var in user_vars:
#                 if var not in variables:
#                     print("Variable " + var + " not found in input file.")
#                     # remove the variable from the list of variables to graph
#                     user_vars.remove(var)
#             if len(user_vars) == 0:
#                 print("No variable(s) specified.")
#                 continue
#             else:
#                 break
# else:
#     user_vars = args.vars
#
# # print the list of variables to graph
# print("\nVariable(s) to graph:")
# for var in user_vars:
#     print(var)

# horizontal_var = args.x
# if horizontal_var not in variables:
#     if args.no_input:
#         exit(1)
#     else:
#         print("Enter the variable to graph on the horizontal axis from the following options:")
#         for var in variables:
#             print(var)
#         while 1:
#             horizontal_var = input("\nEnter the variable to graph on the horizontal axis: ")
#             if horizontal_var not in variables:
#                 print("Variable " + horizontal_var + " not found in input file.")
#                 continue
#             else:
#                 break
#
# # print the variable to graph on the horizontal axis
# print("\nVariable to graph on the horizontal axis: " + horizontal_var)

# xAxis = {}
# yAxis = {}
#
# for sui in user_suis:
#     xAxis[sui] = {}
#     yAxis[sui] = {}
#     for var in user_vars:
#         xAxis[sui][var] = []
#         yAxis[sui][var] = []
#
# with open(args.input_file, 'r') as f:
#     for line in f:
#         line = line.split(',')
#         if line[0] in user_suis:
#             for var in user_vars:
#                 # insert the value so that the x axis is in order
#                 index = 0
#                 # while index < len(xAxis[line[0]][var]) and line[variables.index(horizontal_var)] < xAxis[line[0]][var][index]:
#                 #     index += 1
#                 if line[variables.index(var)] != '':
#                     xAxis[line[0]][var].insert(index, ((datetime.datetime.strptime(line[variables.index(horizontal_var)], "%Y-%m-%d %H:%M:%S") - sui_starts[line[0]]).total_seconds()/1000) % (60*60*24))
#                     yAxis[line[0]][var].insert(index, float(line[variables.index(var)]))
#                 # else:
#                 #     yAxis[line[0]][var].insert(index, 0)
#
# # reverse the lists
# for sui in user_suis:
#     for var in user_vars:
#         xAxis[sui][var].reverse()
#         yAxis[sui][var].reverse()

# show the graph

