import random
import sys
import cv2
import numpy as np
import glob
import os

#Vairables
tInitial = 210
tMin = 220
tMax = 260
fanSpeed = 115
grains = [[0], [tInitial]]
grainsTxt = "Layer,Temp"


#Find and load latest file
latestFile = max(glob.glob('*.gcode'), key=os.path.getctime)
print("Running on " + latestFile)

f = open(latestFile, "r")
gcode = f.read()
f.close()

#Set fan speed
fan = gcode.find("M106 S")
gcode = gcode[:fan+6] + str(fanSpeed) + gcode[fan+9:]

#Find layer count
layers = int(gcode[gcode.find(";LAYER_COUNT:")+len("LAYER_COUNT:")+1:gcode.find(";LAYER:0")])-1

#Initialise output image
h = layers
w = 200
grainsImg = np.full((h, w, 3), 255, np.uint8)

#Generate random layer and temperatures
for x in range(random.randint(int(layers/20), int(layers/10))):
    grains[0].append(2*random.randint(3,int(layers/2)))
    grains[1].append(tMin + 5*random.randint(0,6))

print(grains[0])
print(grains[1])
#Sort layer in ascending order
grains[0].append(layers-1)
grains[0].sort()
grains[0] = list(dict.fromkeys(grains[0]))

#Write layers and temperatures to gcode
for x in range(0, len(grains[0])):
    layer = ";LAYER:" + str(grains[0][x])
    layerLoc = gcode.find(layer) + len(layer)
    layerTemp = str(grains[1][x])
    gcode = gcode[:layerLoc] + "\nM104 S" + layerTemp + gcode[layerLoc:]
    print(layer)
    print(grains[1][x])
    grainsTxt = grainsTxt + "\n" + str(grains[0][x]) + "," + str(grains[1][x])
    for y in range(grains[0][x-1], grains[0][x]):
        grainsImg[y+1, :] = ((tMax - grains[1][x-1])*5, (tMax - grains[1][x-1])*5, (tMax - grains[1][x-1])*5)

#Rotate and show output
grainsImg = cv2.rotate(grainsImg, rotateCode=cv2.ROTATE_180);
cv2.imshow("image", grainsImg);
cv2.waitKey();

#Update screen output of Blender 3
gcode = gcode.replace(";LAYER:", "M117 Printing Layer ")

if not os.path.exists("wood"):
    os.makedirs("wood")

#Save and close file
out = open("wood/" + latestFile , "w")
txtOut = open("wood/" + latestFile + ".csv", "w")
cv2.imwrite("wood/" + latestFile + "_Grain.jpg",grainsImg)
out.write(gcode)
txtOut.write(grainsTxt)
out.close()
txtOut.close()
