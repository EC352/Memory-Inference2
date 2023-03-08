import pandas as pd
from reward_seeking_behavior import aggregated_info, get_info
import os
import cv2

p = 0.9   # Specify the p_cutoff
base_directory = 'C:/Users/emmcle/Documents/Memory-inference/DAP1/Pilot/Behavior/Behavioral-analysis/DLC-trial' # Specify the directory the videos and DLC file can be found
DLC_name = "DLC_resnet50_Memory-InferenceFeb9shuffle1_940000" # Specify the name of the DLC file (without the animal number)
results_directory = 'C:/Users/emmcle/Documents/Memory-inference/DAP1/Pilot/Behavior/Behavioral-analysis/DLC-trial/results' # Specify the directory the results must be stored
video_format = 'mp4' # Specify the video format 
task = 'inference' # Sepcify the task, make sure the soundset file is in the base directory
make_video = True # Specify if a video must be made
inter = 26100
inter16 = 16050

results = pd.DataFrame(
    columns=['animal', 'likelihood_average', 'rsb-set-1', 'rsb-set-2', 'rsb-ITI', 'rsb-set-1-16trials', 'rsb-set-2-16trials', 'rsb-ITI-16trials'])

animal_list= []
for (root, dirs, file) in os.walk(base_directory):
    for f in file:
        if video_format in f:
            animal_ID = f.split('.')
            animal_list.append (animal_ID[0])

if not os.path.exists(results_directory):
    os.makedirs(results_directory)

for animal in animal_list: 
    animal = str(animal)
    df = pd.read_csv(base_directory+'/'
        +animal+DLC_name+'.csv', skiprows=2)
    coords_reward_area = pd.read_csv(base_directory+'/'+animal+'-'      
        +'reward_area'+'.csv')
    soundset = pd.read_csv(base_directory+'/'+
        task+'_set1-set2-frames'+'.csv')

    video = base_directory+'/'+animal+'.'+video_format 
    video_fps = cv2.VideoCapture(video)
    fps = video_fps.get(cv2.CAP_PROP_FPS)
    
    outpath = results_directory+'/' 

    df = get_info(animal, p, df, fps, coords_reward_area,
                  video, outpath, make_video, soundset) 
    results = aggregated_info(df, fps, results, animal, inter, inter16)

results.to_csv(results_directory+'/'+'_results.csv',
                index=False) 