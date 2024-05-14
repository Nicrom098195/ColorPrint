# ColorPrint

This is a program to draw images with a 3D printer. It is designed for Klipper, but you can use it with every firmware you want.
To customize everything you just need to edit the **config.py** file (Every setting is already named and explained in the file).

The script will need at least colormath 3.0.0 and Pillow 9.4.0. You can install them by typing `pip install colormath` and `pip install pillow`.

By running the code you will see a new window open up, asking you to choose an image in your filesystem. It will be automatically resized to the maximum size specified in your ***config.py** file.
After this, the program will automatically generate 4 gcode files, in the __out__ folder. After this you will have to use you printer as a plotter four times, one with every primary color and the last one for black.
