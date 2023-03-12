import cv2
from sys import *
import numpy as np
import json
from readchar import readchar
# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
if len(argv)<2 :
    print("need file name. (input \"output\": visit output.mp4 and label in file named output)")
    exit(0)

filename = argv[1]

framedata=[]
try:
    load = open(filename+"_target_frame", 'r')
    while(True):
        tf = load.readline()
        if tf=="": break
        else:
            framedata+=[ [*map(int, tf[:-1].split(' '))] ]
    load.close()
except FileNotFoundError:
    print("no saved data")
    framedata=[]
#print(framedata)

cap = cv2.VideoCapture(filename+".mp4")

# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")
totalf = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

i = 0 if len(argv)<3 else int(argv[2])
cap.set(1, i)
# Read until video is completed
while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:

        # Display the resulting frame
        cv2.imshow('Frame',frame)
        
        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
        ###############
        # q: quit
        # e: target frame(same to typing 0)
        # [0-9]: target frame with stroke number(see readme)
        # w: not target frame(other key)
        # a: last frame
        # d: next frame
        # f: next 10 frame
        ###############
        print(i)
        label = readchar()
        #print(label)
        if label=='q':
            break
        elif label=='e':
            for tf in framedata:
                if tf[0]==i:
                    del framedata[framedata.index(tf)]
                    #framedata[framedata.index(tf)][1]=0
                    break
            framedata+=[[i, 0]]
        elif label>='0' and label<='9':
            for tf in framedata:
                if tf[0]==i:
                    del framedata[framedata.index(tf)]
                    #framedata[framedata.index(tf)][1]=int(label)
                    break
            framedata+=[[i, int(label)]]
        elif label=='w':
            for tf in framedata:
                if tf[0]==i:
                    del framedata[framedata.index(tf)]
                    break
        elif label=='a':
            if i!=0:
                i-=1
                cap.set(1, i)
            else:
                print("it's the first frame")
            continue
        elif label=='d':
            pass
        elif label=='f':
            if i<totalf-10:
                i+=10
                cap.set(1, i)
            else:
                print("less than 10 frames to the end of video")
            continue
        else:
            pass

        i+=1
    # Break the loop
    else: 
        break

outputdata = open(filename+"_target_frame", 'w')
#json.dump(framedata,outputdata)
for j in framedata:
    outputdata.write(str(j[0])+" "+str(j[1])+"\n")
outputdata.close()
# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
