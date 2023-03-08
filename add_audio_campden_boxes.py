import cv2
import moviepy.editor as mvp
import os

base_directory = "C:/Users/emmcle/Documents/Memory-inference/DAP1/DAP1/005-CORT/Behavior/Batch-1/Conditioning/26-02-2023" # Specify the directory the videos can be found
results_directory = "C:/Users/emmcle/Documents/Memory-inference/DAP1/DAP1/005-CORT/Behavior/Batch-1/Conditioning/Merged-Videos" # Specify the directory the merged videos must be stored
video_format = 'avi' # Specify the video format 
task = 'Conditioning-Blocked' # Sepcify the task
date = '26-02-2023' # Specify the date of the videos (do this for each new date)
start_frame = 0 # Usually the Fiji frame you chose - 1. Check_frame can be run to check for sure
audio_file = "C:/Users/emmcle/Documents/Memory-inference/DAP1/Pilot/Behavior/Audio/conditioning-blocked.m4a"
end_frame = 234500

animal_list= []
for (root, dirs, file) in os.walk(base_directory):
    for f in file:
        if video_format in f:
            animal_ID = f.split('.')
            animal_list.append (animal_ID[0])

if not os.path.exists(results_directory):
    os.makedirs(results_directory)

def cut_video(cut_output, output_name_final_video, video_cap, fps, res, start_frame, audio_file, end_frame):

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(cut_output, fourcc, fps, res)

    video_cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    ret, frame = video_cap.read() 
    count = 0

    while ret:
        out.write(frame)
        ret, frame = video_cap.read()
        count +=1
        if count == end_frame:
            break
    
    out.release()
    video_cap.release()
    cv2.destroyAllWindows

    add_audio(cut_output, output_name_final_video, audio_file, fps)

def add_audio(cut_output, output_name_final_video, audio_file, fps):
    video_cut = mvp.VideoFileClip (cut_output)
    audio = mvp.AudioFileClip (audio_file)
    video_audio = video_cut.set_audio(audio)
    video_audio.write_videofile(output_name_final_video, fps)

for animal in animal_list:
    
    video = base_directory+'/'+animal+'.'+video_format
    cut_output = results_directory+'/'+date+task+animal+'-'+'cut-youcandeletethisone'+'.mp4'
    output_name_final_video = results_directory+'/'+date+task+animal+'-'+'final'+'.mp4'

    video_cap = cv2.VideoCapture(video)
    fps = video_cap.get(cv2.CAP_PROP_FPS)

    frame_width = int(video_cap.get(3))
    frame_height = int(video_cap.get(4))
    res = (frame_width, frame_height)
    
    cut_video(cut_output, output_name_final_video, video_cap, fps, res, start_frame, audio_file, end_frame)




