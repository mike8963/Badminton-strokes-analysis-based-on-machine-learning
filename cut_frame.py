import cv2
import numpy as np
import sys

def cut(filename,n):
    '''
    0----10 11 12----30
            n

    '''

    vc = cv2.VideoCapture(filename)
    print("frame:",vc.get(7))  #check total frames of the video
    fps = int(vc.get(cv2.CAP_PROP_FPS)) # = vc.get(3)
    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)) # = vc.get(4)
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)) # = vc.get(5)

    size = (width, height)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("out_cut.mp4", fourcc, fps, size)

    count = -7
    if(vc.isOpened()):
        while count <8:
            vc.set(cv2.CAP_PROP_POS_FRAMES,n + count)
            ret, frame = vc.read()
            out.write(frame)
            count += 1
    
    vc.release()
    out.release()


if __name__ == '__main__':
    cut(sys.argv[1],int(sys.argv[2]))

