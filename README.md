# SeatViewer
#### An application for reading and analyzing .csv files representing data from the RIT seat experiment

---

## Overview

- Download binary for your platform from the release page
- Run the application with the -h flag to see the available command line options


- To build from source, install the required packages and build with pyinstaller
  - `pip3 install -r requirements.txt`
  - `pyinstaller main.py --hidden-import='PIL._tkinter_finder' --onefile`
    - If you get an error about pyinstaller not recognized on Windows, make sure that the python Scripts path is set correctly in your environment variables
  - On Linux:
    - `./dist/main /path/to/file.csv`
  - On Windows:
    - `dist\main.exe /path/to/file.csv`
