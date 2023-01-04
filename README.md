
# Project Structure
```
├── central 
│   ├── __init__.py
│   ├── db_management.py
│   ├── listenerTCP.py
│   ├── monitor.py
│   ├── server.py
├── client 
│   ├── __init__.py
│   ├── listenerToServer.py 
│   ├── peer.py 
├── .gitignore
├── App.py
├── constants.py
├── Server.py
└── logfile.log
```
#  Requirements
PySimpleGUI <br>
PyQt5  <br>
pymongo


# Setup

Install all required packages in a environment management. In this project, we use Anaconda3 for managing python packet

```
conda create -n env python=3.9
conda activate env
```
Install requirements
```
pip install -r requirements.txt
```

#   Running

First we init the server
```
python Server.py
```

Running App
```
python App.py
```
