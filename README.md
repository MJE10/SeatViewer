# SeatViewer
#### An application for reading and analyzing .csv files representing data from the toilet seat experiment

---

## Overview

- Download binary for your platform from the release page
- Run the application with the -h flag to see the available command line options
- To build from source, install the required packages and build with pyinstaller
  - `pip3 install -r requirements.txt`
  - `pyinstaller main.py --hidden-import='PIL._tkinter_finder' --onefile`
  - `./dist/main /path/to/file.csv`