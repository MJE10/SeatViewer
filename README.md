# SeatViewer
#### An application for reading and analyzing .csv files representing data from the RIT seat experiment

---

## Overview

- Download binary for your platform from the release page
- Run the application with the -h flag to see the available command line options

## Usage

The file used with the program must match the expected format. If you
don't have such a file, you may use generator.py to generate one (specify
the output path of the random file as the first and only argument).

Include the path to the csv file as the first argument to the program. 
All other arguments are optional. Anything required to produce the graph
will be asked in an interactive prompt. You can also use the -h flag to
see the available command line options.

## Building from source

Requirements:
- Python 3
- Tested on Debian Ubuntu and Windows 10

Setup:
- Clone the repository
- Install the required packages
  - `pip3 install -r requirements.txt`

You may run the program using Python or build it to a standalone executable.

To run with Python:
- `python3 main.py /path/to/file.csv`

Or, to see command line options:
- `python3 main.py -h`

You may also use PyInstaller to build the program to an executable.
Note the following:
- PyInstaller cannot cross-compile; it must be compiled for the same platform as the one it is running on
- You must include the hidden import `PIL._tkinter_finder` or matplotlib will not work correctly
- On Windows, your Python3 Scripts folder must be set correctly in your environment variables

Use this command to compile:
- `pyinstaller main.py --hidden-import='PIL._tkinter_finder' --onefile`

This will generate the binary in the `dist` folder. Please do not commit this folder.