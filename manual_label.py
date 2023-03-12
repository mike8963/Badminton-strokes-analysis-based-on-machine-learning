import cv2
from sys import *
import numpy as np
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
            framedata+=[int(tf[:-1])]
    load.close()
    #print(framedata)
except:
    print("no saved data")
    framedata=[]

outputdata = open(filename+"_target_frame", 'w')
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
    #cv2.putText(frame, "frame:"+str(i), (10,40),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
    
    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break
    ###############
    # q: quit
    # e: target frame
    # w: not target frame(default)
    # a: last frame
    # d: next frame
    # f: next 10 frame
    ###############
    print(i)
    label = readchar()
    if label=='q':
        break
    elif label=='e':
        if i not in framedata:
            framedata+=[i]
    elif label=='w':
        if i in framedata:
            del framedata[framedata.index(i)]
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

#json.dump(framedata,outputdata)
for j in framedata:
    outputdata.write(str(j)+"\n")
outputdata.close()
# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
