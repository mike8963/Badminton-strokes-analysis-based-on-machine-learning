import cv2
from PIL import Image
import imagehash
import sys
import os
import numpy as np
import statistics

def maskVideo(video_name):
    
    points = np.array([[0,0],[0,800],[200,800],[400,300],[880,300],[1080,800],[1280,800],[1280,0]])
    black = (0,0,0) # black color
    mask_video = video_name.split('.')[0] + "_masked.mp4"

    vc = cv2.VideoCapture(video_name)

    fps = int(vc.get(cv2.CAP_PROP_FPS)) # = vc.get(3)
    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)) # = vc.get(4)
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)) # = vc.get(5)

    size = (width, height)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(mask_video, fourcc, fps, size)
    
    frame_count = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))

    for i in range(frame_count):
        ret, frame = vc.read()
        
        cv2.fillPoly(frame, [points], black)
        out.write(frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    print(video_name + "mask success")
    vc.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # command:
    # python mask.py [video_name]  含.mp4
    # ex. 
    # python mask.py HSBC_Final_Day_4_3-5.mp4
    
    if(not sys.argv[1]):
        print("please input a video name") # 輸入影片名稱
    else:  
        video_name = os.path.abspath(sys.argv[1])
        print(video_name)
        maskVideo(video_name)
        