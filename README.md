# MapCreator
This application was created through a contract with the Swedish Radiation Safety Authority. Its purpose is to take *.nks-files produced by Nugget and plot the data in those files to a map. If this is in any way unfamiliar, this application is not for you.

## Requirements
This version requires Python 2.7 as well as the following python libraries:

* `numpy`
* `scipy`
* `matplotlib`
* `wxPython`
* `pyproj`
* `cx_Freeze` For creating executables.

If Mapnik is installed and correctly configured with Python bindings and OpenStreetMap data in a PostgreSQL database it is potentially possible to create maps with nice backgrounds. This does require some slight modification of the code however. If the map images intended for Nugget is installed correctly, (`C:/GSD/*` for Windows and `/GSD/*` for other systems) these can be used as backgrounds aswell.

## Compiling and running the application
Compiling the application should be as easy as typing `python2.7 setup.py build` in the `MapCreator` directory. If you want to run the code directly without creating a standalone executable; the `main()`-function is located in `MapCreator.pyw`.

## Documentation
Feel free to write your own. The code should be relatively self explanatory though.

##To-do
MapCreator could use some major (and minor) improvements though the time and money required for this is not available.

##License
This code is provided without a license, do with it whatever you like.
