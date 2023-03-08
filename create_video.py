import cv2
import os

base_directory = "C:/Users/emmcle/Documents/Memory-inference/DAP1/DAP1/005-CORT/Behavior/Batch-1/Conditioning/27-02-2023" # Specify the directory the videos can be found
results_directory = "C:/Users/emmcle/Documents/Memory-inference/DAP1/DAP1/005-CORT/Behavior/Batch-1/Conditioning/Merged-Videos" # Specify the directory the merged videos must be store
video_format = 'AVI' # Specify the video format 
number_of_videos_per_animal = 5
date = '27-02-2023' # Specify the date of the videos 
task = 'Conditioning' # Sepcify the task
start_frame = 222 # Specify the start frame
animals = [443239]

#B1=110
#B2=222
#B3=90

end_frame = 234500
videos = []

for (root, dirs, file) in os.walk(base_directory):
    for f in file:
        if video_format in f:
            video_name = f.split('.')
            videos.append (video_name[0])

def create_video (base_directory, results_directory, date, task, animal, 
video_format, videos, number_of_videos_per_animal, i, count, end_frame):
    cap = cv2.VideoCapture(base_directory+'/'+videos[i]+'.'+video_format)

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    res = (frame_width, frame_height)
    
    path = results_directory+'/'+date+'-'+task+animal+'-'+videos[i]+'-raw'+'.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(path, fourcc, fps, res)

    cap.set (cv2.CAP_PROP_POS_FRAMES, start_frame)

    while(cap.isOpened()):
        ret, frame = cap.read()
        
        if frame is None:
            i += 1
            if i % number_of_videos_per_animal == 0 and i != 0:
                break 
            cap = cv2.VideoCapture(base_directory+'/'+videos[i]+'.'+video_format)
            ret, frame = cap.read()

        out.write(frame)
        count += 1
        if count == end_frame:
            break
        if i % number_of_videos_per_animal == 0 and i != 0:
            break 

    cap.release()
    out.release()
    cv2.destroyAllWindows 
    
for animal in animals:
    animal = str(animal)
    i = 0
    count = 0
    create_video (base_directory, results_directory, date, task, animal, 
    video_format, videos, number_of_videos_per_animal, i, count, end_frame)




