from cmath import nan
import numpy as np
import pandas as pd 
from shapely.geometry import Point 
from shapely.geometry.polygon import Polygon 
import cv2 
import moviepy.editor as mvp

def inaccurate_to_na(df, p):
    """ Sets all values in the dataframe (with bodypart coordinates) lower than the p threshold to NaN

    Parameters
    ----------
    df : pd.Dataframe
        The dataframe with results from DLC
    p : float
        The threshold below which coordinates of bodyparts are set to NaN

    Returns
    -------
    dataframe
        The dataframe with results from DLC without inaccurate coordinates
    """

    for bodypart in ["nose", "head", "center", "tailbase"]: 
        df['x_' + bodypart] = [np.nan if l <
                               p else x_coord for (l, x_coord) in zip(df['l_' + bodypart], df['x_'+bodypart])]
        df['y_' + bodypart] = [np.nan if l <
                               p else y_coord for (l, y_coord) in zip(df['l_' + bodypart], df['y_'+bodypart])]
    return df


def create_polygon_reward(x, y): 
    """ Creates a polygon from corner coordinates

    Parameters
    ----------
    x : float
        X coordinates of corner coordinates
    y : float
        Y coordinates of corner coordinates

    Returns
    -------
    Polygon
        The polygon that is created in this function, 2D array
    """
    coords_reward_area = list(zip(x, y))
    poly_area = Polygon(coords_reward_area)
    x, y = poly_area.exterior.coords.xy
    return poly_area, np.column_stack((x, y))


def reward_seeking(row, frame, poly_area): 
    """ Evaluates if the head is within the set reward_area, and the animal is turned towards the reward module (thus reward seeking behavior)

    Parameters
    ----------
    row : dict
        A row in the dataframe (a frame of the video to be evaluated)
    poly_object : Polygon
        The defined reward seeking area

    Returns
    -------
    Bool
        True is mouse is showing reward_seeking_behavior, False if not
    """
    point_nose = Point(row['x_nose'], row['y_nose'])
    point_head = Point(row['x_head'], row['y_head'])
    point_center = Point(row['x_center'], row['y_center'])
    point_tailbase = Point(row['x_tailbase'], row['y_tailbase'])
    try:
        if point_center.y >= point_tailbase.y and not poly_area.contains(point_head) and not poly_area.contains(point_tailbase):
            return poly_area.contains(point_center)
        else:
            return False
    except (IndexError):
        return False

def cummulative_time(col, fps):
    """ Calculates commulative time that a value is True in a column (thus the animal is seeking reward)

    Parameters
    ----------
    col : series
        A new column of a dataframe
    fps : int
        Frames per second of the video

    Returns
    -------
    series
        A column that shows the cummulative time that a value was True
    """
    col = col.cumsum() 
    col = col/fps 
    col = round (col, 2)
    return col

def write_video(animal, video, outpath, df, fps, coords_reward_area): 
    """ Creates video that shows the reward seeking behavior

    Parameters
    ----------
    animal : int
        The animal number
    video:  path 
        The path to the video 
    outpath: path
        The path the video should be saved in
    df: pd.Dataframe
        The dataframe created by deeplabcut and modified in get_info
    fps: float
        The frames per second of the video
    coord_reward_area: 2D array
        The coordinates of the designated reward area
    """ 

    df['x_nose'] = df['x_nose'].fillna(0)
    df['y_nose'] = df['y_nose'].fillna(0)
    df['x_head'] = df['x_head'].fillna(0) 
    df['y_head'] = df['y_head'].fillna(0)
    df['x_center'] = df['x_center'].fillna(0)
    df['y_center'] = df['y_center'].fillna(0)
    df['x_tailbase'] = df['x_tailbase'].fillna(0)
    df['y_tailbase'] = df['y_tailbase'].fillna(0)

    video = cv2.VideoCapture(video) 

    df['cum_time_reward_seeking1'] = cummulative_time(df['reward_seeking1'],fps)
    df['cum_time_reward_seeking2'] = cummulative_time(df['reward_seeking2'],fps)
    df['cum_time_reward_seekingITI'] = cummulative_time(df['reward_seekingITI'],fps)

    frame_width = int(video.get(3))
    frame_height = int(video.get(4))
    res = (frame_width, frame_height)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(outpath+animal+'_result'+'.mp4', fourcc, fps, res)

    ret, frame = video.read() 

    while(ret):

        frame_nr = video.get(cv2.CAP_PROP_POS_FRAMES) 

        font = cv2.FONT_HERSHEY_SIMPLEX

        text_reward_seeking1 = "Set 1: " + \
            str(df.loc[df.index[round(frame_nr-1)], 'cum_time_reward_seeking1']) + "s  "
        text_reward_seeking2 = "Set 2: " + \
            str(df.loc[df.index[round(frame_nr-1)], 'cum_time_reward_seeking2']) + "s  "
        text_reward_seekingITI = "ITI: " + \
            str(df.loc[df.index[round(frame_nr-1)], 'cum_time_reward_seekingITI']) + "s  "        

        cv2.putText(frame, text_reward_seeking1, (25, 530), font,
                    0.75, (0, 255, 255), 2, cv2.LINE_4)
        cv2.putText(frame, text_reward_seeking2, (300, 530), font,
                    0.75, (0, 0, 255), 2, cv2.LINE_4)
        cv2.putText(frame, text_reward_seekingITI, (600, 530), font,
                    0.75, (255, 255, 255), 2, cv2.LINE_4)

        cv2.polylines(frame, np.int32(
            [coords_reward_area]), isClosed=True, color=(0, 255, 255), thickness=1)

        cv2.circle(frame, (round(df.loc[df.index[round(frame_nr-1)], 'x_nose']), round(
            df.loc[df.index[round(frame_nr-1)], 'y_nose'])), 5, (0, 255, 0), 1)
        cv2.circle(frame, (round(df.loc[df.index[round(frame_nr-1)], 'x_head']), round(
            df.loc[df.index[round(frame_nr-1)], 'y_head'])), 5, (0, 255, 0), 1)
        cv2.circle(frame, (round(df.loc[df.index[round(frame_nr-1)], 'x_center']), round(
            df.loc[df.index[round(frame_nr-1)], 'y_center'])), 5, (255, 255, 255), 1)
        cv2.circle(frame, (round(df.loc[df.index[round(frame_nr-1)], 'x_tailbase']), round(
            df.loc[df.index[round(frame_nr-1)], 'y_tailbase'])), 5, (255, 0, 0), 1)

        out.write(frame)
        ret, frame = video.read()

    video.release()
    out.release()

    cv2.destroyAllWindows()

    outpath_name = outpath+animal+'_result'+'.mp4'
    audio_file = "C:/Users/emmcle/Documents/Memory-inference/DAP1/Pilot/Behavior/Audio/inference.mp3"
    output_name_audio = outpath+animal+'_result'+'audio'+'.mp4'

    add_audio (outpath_name, audio_file, output_name_audio, fps)

def add_audio(outpath_name, audio_file, output_name_audio, fps):
    video_cut = mvp.VideoFileClip (outpath_name)
    audio = mvp.AudioFileClip (audio_file)
    video_audio = video_cut.set_audio(audio)
    video_audio.write_videofile(output_name_audio, fps)

def get_info(animal, p, df, fps, coords_reward_area, video, outpath, make_video, soundset): 
    """ Takes in DLC dataframe and modifies it to show in which frames the animal is showing reward seeking behavior, 
    also creates video to display this.

    animal: int
        The animalnumber
    p : float
        The threshold below which coordinates of bodyparts are set to NA
    offset: int
        Amount of pixels the polygon is scaled with
    df : pd.Dataframe
        The dataframe created by deeplabcut and modified in get_info
    fps: float
        The frames per second of the video
    coords_reward_area: csv file
        Csv files containing the coordinates from the corners of the designated reward area
    video: str
        The path to the video file
    make_video: bool, optional
        A flag used to indicate if a video that shows reward seeking behavior times and area
    soundset: pd.Dataframe
        The dataframe containing which frame belongs to which sound set

    Returns
    -------
    pd.Dataframe
        A dataframe that contains all extra information (how long the animal is showing reward seeking behavior)
    """

    df = df.rename(columns={'coords': 'frame', 'x': 'x_left-ear', 'y': 'y_left-ear', 'likelihood': 'l_left-ear',
                            'x.1': 'x_right-ear', 'y.1': 'y_right-ear', 'likelihood.1': 'l_right-ear',
                            'x.2': 'x_nose', 'y.2': 'y_nose', 'likelihood.2': 'l_nose', 
                            'x.3': 'x_center', 'y.3': 'y_center', 'likelihood.3': 'l_center',
                            'x.4': 'x_left-side', 'y.4': 'y_left-side', 'likelihood.4': 'l_left-side',
                            'x.5': 'x_right-side', 'y.5': 'y_right-side', 'likelihood.5': 'l_right-side',
                            'x.6': 'x_tailbase', 'y.6': 'y_tailbase', 'likelihood.6': 'l_tailbase',
                            'x.7': 'x_tailtip', 'y.7': 'y_tailtip', 'likelihood.7': 'l_tailtip',
                            'x.8': 'x_head', 'y.8': 'y_head', 'likelihood.8': 'l_head'})
    soundset = soundset.rename(columns={'0': 'frame', '0.0': 'set'})
    
    extracted_set = soundset['set'] #When the set is 1.0: set 1 sound, when the set is 2.0: set 2 sound, when the set is 0.0: ITI
    df = df.join(extracted_set)

    poly_area, coords_reward_area_og = create_polygon_reward(coords_reward_area.X, coords_reward_area.Y) 
    
    df = inaccurate_to_na(df, p)

    """This bottom section calls the reward_seeking function, and says true if reward_seeking returns True,
    also it distinguishes between the different sound sets"""

    df['reward_seeking1'] = df.apply (reward_seeking, args=(poly_area, poly_area), axis=1)
    df['reward_seeking2'] = df.apply (reward_seeking, args=(poly_area, poly_area), axis=1)
    df['reward_seekingITI'] = df.apply (reward_seeking, args=(poly_area, poly_area), axis=1)

    df.loc[df.set == 2.0, 'reward_seeking1'] = False
    df.loc[df.set == 0.0, 'reward_seeking1'] = False

    df.loc[df.set == 1.0, 'reward_seeking2'] = False
    df.loc[df.set == 0.0, 'reward_seeking2'] = False

    df.loc[df.set == 1.0, 'reward_seekingITI'] = False
    df.loc[df.set == 2.0, 'reward_seekingITI'] = False

    if make_video:
        write_video(animal, video, outpath, df, fps, coords_reward_area)

    return df

def aggregated_info(df, fps, results, animal, inter, inter16):
    """ Create a dataframe with all summary results from the analysis

    Parameters
    ----------
    df : pd.Dataframe
        The dataframe created by deeplabcut and modified in get_info
    fps: float # is fps float or int?
        The frames per second of the video
    results: pd.Dataframe
        The dataframe to which summary results form all animals are added 
    animal: int
        The animalnumber

    Returns
    -------
    pd.Dataframe
        A dataframe with summary results from an animal added to it
    """

    total_time_reward_seeking1 = len(df[df['reward_seeking1']].loc[:inter]) / fps
    total_time_reward_seeking2 = len(df[df['reward_seeking2']].loc[:inter]) / fps
    total_time_reward_seekingITI = len(df[df['reward_seekingITI']].loc[:inter]) / fps

    inter_time_reward_seeking1 = len(df[df['reward_seeking1']].loc[:inter16]) / fps
    inter_time_reward_seeking2 = len(df[df['reward_seeking2']].loc[:inter16]) / fps
    inter_time_reward_seekingITI = len(df[df['reward_seekingITI']].loc[:inter16]) / fps

    likelihood_average = sum(df['l_nose'])/len(df['l_nose'])

    results=results.append({'animal':animal, 'likelihood_average':likelihood_average,
                            'rsb-set-1':total_time_reward_seeking1, 
                            'rsb-set-2':total_time_reward_seeking2,
                            'rsb-ITI':total_time_reward_seekingITI,
                            'rsb-set-1-16trials':inter_time_reward_seeking1, 
                            'rsb-set-2-16trials':inter_time_reward_seeking2,
                            'rsb-ITI-16trials':inter_time_reward_seekingITI,
                            }      
                            , ignore_index=True)
     
    return results

