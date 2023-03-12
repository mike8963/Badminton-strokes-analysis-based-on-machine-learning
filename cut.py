import cv2
import numpy as np

vc = cv2.VideoCapture("../outputVID/output1.mp4")

fps = int(vc.get(cv2.CAP_PROP_FPS)) # = vc.get(3)
width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)) # = vc.get(4)
height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)) # = vc.get(5)

size = (width, height)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("output.mp4", fourcc, fps, size)
origin = cv2.VideoWriter("origin.mp4", fourcc, fps, size)
out_gray = cv2.VideoWriter("output_gray.mp4", fourcc, fps, size)

while vc.isOpened():
    ret, frame = vc.read()
    origin.write(frame)
    # 下面之後包成function比較好的感覺
    cv2.imwrite('./original.jpg',frame) # 拿來比對 後面可以拿掉 
    
    # 場線偵測 #
    
    # RGB to gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # gaussian 
    kernel_size = 7
    blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
    #canny
    canny = cv2.Canny(blurred, 30,100)

    #mask

    points = np.array([[0,0],[0,800],[200,800],[350,500],[350,360],[930,360],[930,500],[1080,800],[1280,800],[1280,0]])
    black = (0,0,0)
    cv2.fillPoly(canny, [points], black)


    # hough
    rho = 1
    theta = np.pi / 180
    threshold = 1
    min_line_lehgth = 35
    max_line_gap = 0.5

    line_image = np.copy(frame)*0

    lines = cv2.HoughLinesP(canny, rho, theta, threshold, np.array([]),min_line_lehgth,max_line_gap)

    for line in lines:
        for x1,y1,x2,y2, in line:
            cv2.line(line_image,(x1,y1),(x2,y2),(0,0,255),10)
            cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),10)
    color_edges = np.dstack( (canny, canny, canny))
    combo = cv2.addWeighted(color_edges,0.8,line_image,1,0)




    # result 檢查

    out.write(frame)
    out_gray.write(combo)
    
    cv2.imshow('frame', frame)
    cv2.imshow('combo',combo)

    #quit key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vc.release()
out.release()
cv2.destroyAllWindows()