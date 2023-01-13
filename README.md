# FleetIAS

## Dev documentation
### Generate gui
1. Edit ``gui.gui`` in QT Designer
2. Run ``python -m PyQt5.uic.pyuic -x gui.ui -o mainwindow.py`` in ``frontend/``
3. Add button callbacks etc. in ``mainwindow.py``

## Manual
### Installation
- Create Python virtual environment: ``python3 -m venv venv ``
- Start virtual enviromnent: ``source venv/bin/activate`` (Linux)
- Install Python packages into virtual environment: ``pip3 install -r requirements.txt``

### Run
``python3 /frontend/mainwindow.py``