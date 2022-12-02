# FleetIAS

## Dev documentation
### Generate gui
1. Edit ``gui.gui`` in QT Designer
2. Run ``python -m PyQt5.uic.pyuic -x gui.ui -o mainwindow.py`` in ``frontend/``
3. Add following lines in ``mainwindow.py`` before the line ``    MainWindow.show()`` (very bottom of file)
```python
    guiManager = GUIManager(ui)
    guiManager.connectCallbackFunction()
    guiManager.addComboBoxItems()
```
4. Add button callbacks etc. in ``frontend/guimanager.py``

## Manual
### Installation
- Create Python virtual environment: ``python3 -m venv venv ``
- Start virtual enviromnent: ``source venv/bin/activate`` (Linux)
- Install Python packages into virtual environment: ``pip3 install -r requirements.txt``

### Run
``python3 /frontend/mainwindow.py``