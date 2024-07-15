# transcription-webapp

## Name
Offline Automatic Speech Recognition Application

## Description
This application was developed using streamlit. The purpose of this project is to allow for Automatic Speech Recognition without uploaded audio files to a company server. This alleviates any issues with ethics with uploaded sensitive data.

## Visuals
The overall architecture of the webapp is provided as following:

![Architecture of the Webapp](webapp-architecture.png)

## Getting started

This package is meant to be run with a python virtual environment.

To make a virtual environment and download all the requirements:

```
cd repository
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You will also need to install ffmpeg:

```
sudo apt install ffmpeg
```

## Running the Webapp

The basic commands for running the webapp are:

```
streamlist run main.py
```

If you want to run on a specific port, say 8051 in this example:

```
streamlit run main.py --server.port 8051
```

***

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
