from PIL import Image
from colormath.color_objects import sRGBColor, CMYKColor
from colormath.color_conversions import convert_color
import math
import os
from tkinter import filedialog
from datetime import datetime

def curTime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def browseImage():
    filename = filedialog.askopenfilename(filetypes=[("Image",".jpg"),("Image",".jpeg"),("Image",".png")])
    return filename

def circleCoords(bx, by, d, np=30):
    r = d / 2
    return [(bx + r * math.cos(2 * math.pi * i / np), by + r * math.sin(2 * math.pi * i / np)) for i in range(np + 1)]

def cc(rgb):
    rgb_color = sRGBColor(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    return convert_color(rgb_color, CMYKColor).get_value_tuple()
    
def cr(cmyk):
    cmyk_color = CMYKColor(*cmyk)
    rgb_color = convert_color(cmyk_color, sRGBColor)
    return (int(rgb_color.clamped_rgb_r * 255), int(rgb_color.clamped_rgb_g * 255), int(rgb_color.clamped_rgb_b * 255))


def pixels(image, max_size):
    width, height = image.size
    if width > height:
        ratio = max_size / width
    else:
        ratio = max_size / height
    new_width = int(width * ratio)
    new_height = int(height * ratio)
    image = image.resize((new_width, new_height))
    end=[]
    for y in range(new_height):
        k=[]
        for x in range(new_width):
            k.append(image.load()[x,new_height-(y+1)])
        end.append(k)
    return end

name=browseImage() #Drawing's name

pxs=4 #Pixel size

#Max size (mm), it won't be the exact picture size, but it will be the maximum size the picture can reach (the actual size will be the smallest multiple of pxs)
ms=80

#Size multiplier, multiplies the size of the pixel, to get smaller ones, or even to get some pixels to go over other ones.
smp=0.8

#Pixels array
ar=pixels(Image.open(name), int((ms//pxs)))

name=name.split(".")[0].split("/")[len(name.split(".")[0].split("/"))-1]

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

wx=len(ar[0])*pxs
wy=len(ar)*pxs

sx=(bx-wx)/2
sy=(by-wy)/2

mx=235 #Max X
my=222 #Max Y
if sx+wx+xos>mx:
    sx+=(sx+wx+5)-mx

if sy+wy+yos>my:
    sy+=(sy+wy+5)-my
    
#Shapes:
#0:square
#1:circle
shape=1

print("Start at",sx+xos,sy+yos,", end at",sx+wx+xos,sy+wy+yos)
print("Size:",wx,wy)

# Start g-code (not your slicer's one, because we aren't gonna need heating)
sgc="""G28
G90
G1 F10000
TIMELAPSE_TAKE_FRAME

; Created on Color image engine
"""

sgc=sgc+'; On date '+curTime()+'\n; {"pxs":'+str(pxs)+',"smp":'+str(smp)+',"rmp":'+str(rmp)+',"ymp":'+str(ymp)+',"bmp":'+str(bmp)+',"kmp":'+str(kmp)+'}\n\n'

gr=sgc+"G1 Z"+str(uz)+"\n"
gb=sgc+"G1 Z"+str(uz)+"\nG1 X"+str(sx+xos-bos)+" Y"+str(sy+yos-bos)+"\nG1 Z"+str(dz)+"\nG1 X"+str(sx+wx+xos+bos)+"\nG1 Y"+str(sy+wy+yos+bos)+"\nG1 X"+str(sx+xos-bos)+"\nG1 Y"+str(sy+yos-bos)+"\nG1 Z"+str(uz)+"\n"
gy=sgc+"G1 Z"+str(uz)+"\n"
gk=sgc+"G1 Z"+str(uz)+"\n"


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

tot=len(ar)*len(ar[0])
#act:tot=x:100 => x=act*100/tot

for y in range(len(ar)):
    gr=gr+"\n"+lgc+"\n"
    gy=gy+"\n"+lgc+"\n"
    gb=gb+"\n"+lgc+"\n"
    gk=gk+"\n"+lgc+"\n"
    for x in range(len(ar[y])):
        print("Generating g-code",str(round((y*len(ar[0])+x)*100/tot))+"%                    ",end="\r")
        b,r,yc,k=cc(ar[y][x])
        r=pxs*r*smp*rmp
        yc=pxs*yc*smp*ymp
        b=pxs*b*smp*bmp
        k=pxs*k*smp*kmp
        if r>0:
            if shape==0:
                gr=gr+"\nG1 X"+str(sx+x*pxs+((pxs-r)/2)+xos)+" Y"+str(sy+y*pxs+((pxs-r)/2)+yos)+" Z"+str(uz)+"\nG1 Z"+str(dz-r/23)+"\nG91\nG1 X"+str(r)+"\nG1 Y"+str(r)+"\nG1 X-"+str(r)+"\nG1 Y-"+str(r)+"\nG90\nG1 Z"+str(uz)
            elif shape==1:
                ps=circleCoords(sx+x*pxs+pxs/2+xos,sy+y*pxs+pxs/2+yos,r)
                gr=gr+"\nG1 X"+str(ps[0][0])+" Y"+str(ps[0][1])+" Z"+str(uz)+"\nG1 Z"+str(dz)+"\n"
                for i in ps:
                    gr=gr+"G1 X"+str(i[0])+" Y"+str(i[1])+"\n"
                gr=gr+"G1 Z"+str(uz)
        if b>0:
            if shape==0:
                gb=gb+"\nG1 X"+str((sx+x*pxs)+((pxs-b)/2)+xos)+" Y"+str(sy+y*pxs+((pxs-b)/2)+yos)+" Z"+str(uz)+"\nG1 Z"+str(dz-b/23)+"\nG91\nG1 X"+str(b)+"\nG1 Y"+str(b)+"\nG1 X-"+str(b)+"\nG1 Y-"+str(b)+"\nG90\nG1 Z"+str(uz)
            elif shape==1:
                ps=circleCoords(sx+x*pxs+pxs/2+xos,sy+y*pxs+pxs/2+yos,b)
                gb=gb+"\nG1 X"+str(ps[0][0])+" Y"+str(ps[0][1])+" Z"+str(uz)+"\nG1 Z"+str(dz)+"\n"
                for i in ps:
                    gb=gb+"G1 X"+str(i[0])+" Y"+str(i[1])+"\n"
                gb=gb+"G1 Z"+str(uz)
        if yc>0:
            if shape==0:
                gy=gy+"\nG1 X"+str(sx+x*pxs+((pxs-yc)/2)+xos)+" Y"+str(sy+y*pxs+((pxs-yc)/2)+yos)+" Z"+str(uz)+"\nG1 Z"+str(dz-yc/23)+"\nG91\nG1 X"+str(yc)+"\nG1 Y"+str(yc)+"\nG1 X-"+str(yc)+"\nG1 Y-"+str(yc)+"\nG90\nG1 Z"+str(uz)
            elif shape==1:
                ps=circleCoords(sx+x*pxs+pxs/2+xos,sy+y*pxs+pxs/2+yos,yc)
                gy=gy+"\nG1 X"+str(ps[0][0])+" Y"+str(ps[0][1])+" Z"+str(uz)+"\nG1 Z"+str(dz)+"\n"
                for i in ps:
                    gy=gy+"G1 X"+str(i[0])+" Y"+str(i[1])+"\n"
                gy=gy+"G1 Z"+str(uz)
        if k>0:
            if shape==0:
                gk=gk+"\nG1 X"+str(sx+x*pxs+((pxs-k)/2)+xos)+" Y"+str(sy+y*pxs+((pxs-k)/2)+yos)+" Z"+str(uz)+"\nG1 Z"+str(dz-k/23)+"\nG91\nG1 X"+str(k)+"\nG1 Y"+str(k)+"\nG1 X-"+str(k)+"\nG1 Y-"+str(k)+"\nG90\nG1 Z"+str(uz)
            elif shape==1:
                ps=circleCoords(sx+x*pxs+pxs/2+xos,sy+y*pxs+pxs/2+yos,k)
                gk=gk+"\nG1 X"+str(ps[0][0])+" Y"+str(ps[0][1])+" Z"+str(uz)+"\nG1 Z"+str(dz)+"\n"
                for i in ps:
                    gk=gk+"G1 X"+str(i[0])+" Y"+str(i[1])+"\n"
                gk=gk+"G1 Z"+str(uz)
        
gr=gr+egc
gy=gy+egc
gb=gb+egc
gk=gk+egc

print("Gcode generated. Saving files...                        ", end="\r")

try:
    os.mkdir("out/"+name)
except:
    pass

if os.path.exists("out/"+name+"/magenta.gcode"):
  os.remove("out/"+name+"/magenta.gcode")
if os.path.exists("out/"+name+"/yellow.gcode"):
  os.remove("out/"+name+"/yellow.gcode")
if os.path.exists("out/"+name+"/cyan.gcode"):
  os.remove("out/"+name+"/cyan.gcode")
if os.path.exists("out/"+name+"/black.gcode"):
  os.remove("out/"+name+"/black.gcode")

with open("out/"+name+"/magenta.gcode", "w") as red:
    red.write(gr)

with open("out/"+name+"/yellow.gcode", "w") as yellow:
    yellow.write(gy)

with open("out/"+name+"/cyan.gcode", "w") as blue:
    blue.write(gb)

with open("out/"+name+"/black.gcode", "w") as black:
    black.write(gk)

print("Done saving files.                                                         ")
