pxs=4 #Pixel size

ms=80 #Max size (mm), it won't be the exact picture size, but it will be the maximum size the picture can reach (the actual size will be the smallest multiple of pxs)

smp=0.8 #Size multiplier, multiplies the size of the pixel, to get smaller ones, or even to get some pixels to go over other ones.

#Offsets (mm)
dz=13.7 #Z down
uz=18 #Z up
xos=60 #X offset
yos=0 #Y offset
bos=2 #Border offset from drawing

bx=220 #Bed X
by=220 #Bed Y

#Colors multipliers
rmp=1
ymp=1
bmp=1
kmp=0.6

mx=235 #Max X pos
my=222 #Max Y pos

#Shape for every pixel:
#0:square
#1:circle
shape=1

# Start g-code (not your slicer's one, because we aren't gonna need heating)
sgc="""G28
G90
G1 F10000
TIMELAPSE_TAKE_FRAME

; Created on Color image engine
"""

# End g-code (not your slicer's one, because we aren't gonna need cooling)
egc="""


G90
G1 Z50 F400
G1 X0 Y222 F7000
M300
M300
M300
TIMELAPSE_TAKE_FRAME
G4 P3000
LOAD_PEN"""

# Gcode to put between every layer
lgc="""
TIMELAPSE_TAKE_FRAME
"""
