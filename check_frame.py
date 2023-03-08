import cv2
import os

base_directory = "C:/Users/emmcle/Documents/Memory-inference/DAP1/Pilot/Behavior/Batch-5/Inference" # Specify the directory the videos can be found
video_format = 'AVI' # Specify the video format 
task = 'Inf' # Specify the task (needed for the audio file)
start_frames = [190, 191, 192, 193, 194, 195, 196, 197, 198] # Enter the to tested frame number (usually Fiji frame -2 and + 2, seperated by a comma)
#36=
#37=2
#38=
#39=2
#40=
#41=

animal_list= []
for (root, dirs, file) in os.walk(base_directory):
    for f in file:
        if video_format in f:
            animal_ID = f.split('.')
            animal_list.append (animal_ID[0])

def show_frame (start_frames, base_directory, animal, video_format, task):

    for start_frame in start_frames:
        video_path = base_directory+'/'+animal+'.'+video_format
        video_cap = cv2.VideoCapture (video_path)

        video_cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        ret, frame = video_cap.read()

        name = task+'-'+animal+'-'+str(start_frame)

        cv2.imshow(name, frame); cv2.waitKey (0)

for animal in animal_list:
    show_frame(start_frames, base_directory, animal, video_format, task)

            
