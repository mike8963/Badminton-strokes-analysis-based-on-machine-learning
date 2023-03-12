import cv2
from PIL import Image
import imagehash
from moviepy.editor import VideoFileClip
import sys
import os
import numpy as np
import statistics

def hashToStr(imghash):
    s = []
    for i in range(8):
        for j in range(8):
            y = int(imghash[i][j])
            s.append(str(y))

    return "".join(s)

def strToHash(str_img):
    l = []
    if len(str_img) != 64:
        emsg = 'Expected str string size of {}'
        raise ValueError(emsg.format(64))
    ll = []
    for i in range(len(str_img)):       
        if len(ll) == 8:
            l.append(ll)
            ll = []
            ll.append(int(str_img[i]) > 0)
        else:
            ll.append(int(str_img[i]) > 0)
    l.append(ll)
    return imagehash.ImageHash(np.array(l))

def fine_basic_image(clip,fps):
    im0 = ""
    hash_list = []

    for i,img in enumerate(clip.iter_frames(fps)):
        if i == 0:
            im0 = img
        time = (i) / fps
        result, hash_value = isSimilar(im0, img)
        hash_list.append(hashToStr(hash_value.hash))
        im0 = img
    hash_appear = dict((a,hash_list.count(a)) for a in hash_list)

    for i,j in hash_appear.items():
        if j == max(hash_appear.values()):
            return strToHash(i)
    
def isSimilar(img1, img2):

	# OpenCV to PIL image
    img1 = Image.fromarray(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))  
    img2 = Image.fromarray(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)) 
    
    # 前後幀的平均hash值
    n0 = imagehash.average_hash(img1) 
    n1 = imagehash.average_hash(img2)
     
    # hash值最小相差多少則判斷為不相似，可以根據需要自定義
    cutoff = 5

    flag = True
    if n0 - n1 > cutoff:
        flag = False

    return flag ,n0

def sliceVideo(clip, fps, video_name):
    im0 = ""			# 目標幀
    start_time = 0      # 片段開始時間
    end_time = 0        # 片段結束時間
    video_count = 1     # 影片編號
    success_durations = []	# 成功片段時間列表
    skip_durations = []	# 排除片段時間列表
    distance_list = []   #紀錄各幀與基準幀的差異值
    basic_value = fine_basic_image(clip,fps) #作為判斷是否為需要用的影片的基準

    for i,img in enumerate(clip.iter_frames(fps)):
        if i == 0: 
            im0 = img
        time = (i) / fps

        result, hash_value = isSimilar(im0, img)
        distance_list.append(hash_value - basic_value)
        if not result:	# 結果為不相似
            end_time = (i-1) / fps
            print(start_time, end_time)
            if start_time == end_time:	# 排除情況，開始時間和結束時間相同的話moviepy會報錯；也可以根據需要篩選時長大於多少的片段
                skip_durations.append([start_time, end_time])
            else:
                average_distance = statistics.mean(distance_list)
                print(average_distance)
                if average_distance <= 5:
                    clip.subclip(start_time, end_time).write_videofile(f"../video_clip_output/successful_clip/{video_name}-{video_count}.mp4")
                    print("success")
                    video_count += 1
                
                success_durations.append([start_time, end_time])
            start_time = time

            distance_list.clear()
        im0 = img
    # 沒有觸發不相似的最後一個片段
    end_time = clip.duration
    if start_time == end_time:  # 排除情况
        skip_durations.append([start_time, end_time])
    else:
        average_distance = statistics.mean(distance_list)
        print(average_distance) #這行可以砍掉 除錯用
        if average_distance <= 5:
            clip.subclip(start_time, end_time).write_videofile(f"../video_clip_output/successful_clip/{video_name}-{video_count}.mp4")
            print("success") #這行可以砍掉 除錯用
        
        success_durations.append([start_time, end_time])
        distance_list.clear()

    return success_durations, skip_durations

if __name__ == "__main__":
    
    # python cut_special.py outputVID/output1.mp4
    if(not sys.argv[1]):
        print("please input a video name") # 輸入從當前目錄開始算的path
    else:
        if not os.path.isdir("video_clip_output"):
            os.mkdir("video_clip_output")
        if not os.path.isdir("video_clip_output/successful_clip"):
            os.mkdir("video_clip_output/successful_clip")
        if not os.path.isdir("video_clip_output/useless_clip"):
            os.mkdir("video_clip_output/useless_clip")
            
        clip = VideoFileClip(sys.argv[1])
        video_name = os.path.basename(sys.argv[1]).split('.')[0]
        
        success, skip = sliceVideo(clip, clip.fps,video_name)
        print(f"成功片段：\n{success}\n\n排除片段：\n{skip}\n")
        