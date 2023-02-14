"""
SPEAR Challenge

Creates the Scenes for Tascar.
Input: Current dataset, session and spear path
Output Gen: A single tascar .tsc file is computed with many scenes.
Output Run: all the .wav files for all the scenes.

Scene creation fct:
- strToStr: Small function to add "" in our strings for tascar.
- block_table: Add reflecting surfaces (table).
- block_reverb: Add reverb, early (walls) and late (FDN).
- block_sourceID: Add various sources (talkers) to the scene.
- block_receiver_hoa: Add the ambisonic receiver.
- block_receiver_hrtf: Add the HRTF receiver.
- block_noise: Add noise (10 distributed loudspeakers).
- tascar_60s_check: Verify that the output audio file is exactly 60s long.

- SPEAR_tascarSceneGen: Use the blocks above to create on the fly a tascar file with the desired parameters. 
                        The tascar file contains multiple scenes including an anechoic condition one.
- SPEAR_tascarSceneRun: Run the above file for the anechoic case, the noise only case and the source only case. 
                        The audio mixture is made in post processing.
                        Include the option to run the convolution to output the audio array using the HOA file. Requires the ATFs.

"""

import os
import time
import pandas as pd
import soundfile as sf
from pathlib import Path
from pathlib import PurePath
from fct_PathFinder import PathFinder
import random
import tempfile
import platform


###### Global Parameters
path_blocks = PurePath(os.path.dirname(os.path.realpath(__file__)), 'Scenes_blocks')
source_lvl = 80
ls_level_plus = -13 # what we add on top of source_lvl for the loudspeakers in D2
hoa_order = 15
option = 'Tascar'
fs_out = 48000


###### Functions for each blocks of the scene

### Small function to add "" in our strings for tascar
def strToStr(blockname):
    return '"' + blockname + '"'


### REFLECTING SURFACE/TABLE
def block_table(t_scattering):

    file_table = PurePath(path_blocks, 'Block_t.tsc')
    fin = open(file_table)
    temp_table = fin.read()
    fin.close()

    # Define table scattering (0 by default)
    table = temp_table.format(t_scattering = strToStr(str(t_scattering)),
                                )

    return table


### REVERB
def block_reverb(room_x, 
                 room_y,
                 room_z, 
                 center_x, 
                 center_y, 
                 center_z, 
                 absorption,
                 damping,
                #  t60,
                 ):

    file_w =  PurePath(path_blocks, 'Block_w.tsc')
    fin = open(file_w)
    temp_reverb_w = fin.read()
    fin.close()

    reverb_w = temp_reverb_w.format(room_x = str(room_x),
                                    room_y = str(room_y),
                                    room_z = str(room_z),
                                    center_x = str(center_x),
                                    center_y = str(center_y),
                                    center_z = str(center_z),
                                    )

    file_r =  PurePath(path_blocks, 'Block_r.tsc')
    fin = open(file_r)
    temp_reverb_r = fin.read()
    fin.close()

    reverb_r = temp_reverb_r.format(room_x = str(room_x),
                                    room_y = str(room_y),
                                    room_z = str(room_z),
                                    center_x = str(center_x),
                                    center_y = str(center_y),
                                    center_z = str(center_z),
                                    absorption  = strToStr(str(absorption)),
                                    damping = strToStr(str(damping)),
                                    # t60         = strToStr(str(t60)),
                                    )

    # reverb = reverb_w + reverb_r
    return reverb_w, reverb_r


### SOURCES IDX
def block_sourceID(idd):

    file_source   =  PurePath(path_blocks, f'Block_source.tsc')

    fin = open(file_source)
    temp_source = fin.read()
    fin.close()

    # Name of the source block
    source_name = f'ID{idd}'
    
    # Path of the csv position and orientation files.
    source_pos = f'pos_ID{idd}.csv'
    source_ori = f'ori_ID{idd}.csv'

    # Path of the audio files. depending on whether we use the original ones or the MuteFade ones
    source_audio = f'audio_ID{idd}.wav'

    source = temp_source.format(source_name  = strToStr(source_name),
                                source_level = strToStr(str(source_lvl)),
                                source_pos   = strToStr(str(source_pos)),
                                source_ori   = strToStr(str(source_ori)),
                                source_audio = strToStr(str(source_audio))
                                )
    
    return source



### RECEIVER
def block_receiver_hoa():
    idd = 2
    receiver_pos = f'pos_ID{idd}.csv'
    receiver_ori = f'ori_ID{idd}.csv'

    receiver_name = 'Ambisonic'
    file_receiver =  PurePath(path_blocks, 'Block_hoa.tsc')
        
    fin = open(file_receiver)
    temp_receiver = fin.read()
    fin.close()

    receiver = temp_receiver.format(receiver_name = strToStr(receiver_name),
                                    receiver_pos  = strToStr(str(receiver_pos)),
                                    receiver_ori  = strToStr(str(receiver_ori)),
                                    hoa_order     = str(hoa_order),
                                    )

    return receiver

### bonus HRTF block to create a separate tascar file that can be investigated with the gui (hoa does not work with the gui)
def block_receiver_hrtf():
    idd = 2
    receiver_pos = f'pos_ID{idd}.csv'
    receiver_ori = f'ori_ID{idd}.csv'

    receiver_name = 'HRTF'
    file_receiver =  PurePath(path_blocks, 'Block_h.tsc')
        
    fin = open(file_receiver)
    temp_receiver = fin.read()
    fin.close()

    receiver = temp_receiver.format(receiver_name = strToStr(receiver_name),
                                    receiver_pos  = strToStr(str(receiver_pos)),
                                    receiver_ori  = strToStr(str(receiver_ori))
                                    )

    return receiver


### NOISE
def block_noise(center_x,
                center_y,
                ls_x,
                ls_y,
                ls_z,
                noise_lvl,
                path_spear,
                session_n,
                ):

    if session_n<10:
        set_n = 'Train'
    elif session_n<13:
        set_n = 'Dev'
    else:
        set_n = 'Eval'

    noise_path_in  = PurePath(PathFinder(0, 0, 'noise', path_spear=path_spear), set_n)

    noise_files_out = list(Path(noise_path_in).glob(f'*.wav'))
    noise_files_out = [f for f in noise_files_out if f.stem[0]!='.']

    ### Load single loudspeaker and create the 10 ones (maybe less loudspeakers if small room)
    file_loudspeaker =  PurePath(path_blocks, 'Block_l10_single.tsc')

    fin = open(file_loudspeaker)
    temp_loudspeaker = fin.read()
    fin.close()
    
    ls_num = len(ls_x)
    noise_file = random.choices(noise_files_out, k=ls_num)
    path_out = f'../../../../../../Miscellaneous/AmbientNoise/{set_n}/'

    loudspeakers = ''
    for ls in range(ls_num):
        loudspeaker = temp_loudspeaker.format(ls_num  = ls,
                                              ls_x = strToStr(str(center_x+ls_x[ls])),
                                              ls_y = strToStr(str(center_y+ls_y[ls])),
                                              ls_z = strToStr(str(ls_z[ls])),
                                              noise_level  = strToStr(str(noise_lvl[ls])),
                                              noise_file = strToStr(path_out+str(noise_file[ls].name)),
                                              )
        loudspeakers += loudspeaker

    ### Upload the 10 loudspeakers to the final block (maybe less loudspeakers if small room)
    # file_noise =  PurePath(path_blocks, 'Block_l.tsc')

    # fin = open(file_noise)
    # temp_noise = fin.read()
    # fin.close()

    # noise = temp_noise.format(loudspeakers = loudspeakers,
    #                           center_x = str(center_x),
    #                           center_y = str(center_y),
    #                           )

    return loudspeakers






###### Main fct for Scene Generation
def SPEAR_tascarSceneGen(dataset_n, session_n, path_spear):

    if dataset_n==1: raise 'Dataset 1 do not have Tascar simulations.'

    ### List of minute of current dataset
    path_tascar_LINUX = PathFinder(dataset_n, session_n, option, path_spear=path_spear)
    path_walk = [Path(x[0]) for x in os.walk(str(path_tascar_LINUX))]
    path_walk.pop(0)
    path_walk.sort()
    minutes = [walk.stem for walk in path_walk if walk.stem[0]!='.']

    for minute in minutes:
        ### Working path for the current output
        path_tascar_linux = PurePath(path_tascar_LINUX, minute)

        if dataset_n == 2:
            ### Define here all the new parameters that can be varied for D3
            t_scattering = 0
            room_x = 6.11
            room_y = 7.74
            room_z = 3.44
            center_x = 0.5
            center_y = -0.91
            center_z = room_z/2
            absorption = 0.6
            damping = 0.3
            # t60 = 0.6
            ls_levels= [source_lvl+ls_level_plus, source_lvl+ls_level_plus, source_lvl+ls_level_plus, source_lvl+ls_level_plus, source_lvl+ls_level_plus, source_lvl+ls_level_plus, source_lvl+ls_level_plus, source_lvl+ls_level_plus, source_lvl+ls_level_plus, source_lvl+ls_level_plus]
            ls_x_all = [  room_x/2-1,  room_x/2-3,  room_x/2-5,  room_x/2-5,    room_x/2-5,  room_x/2-5,    room_x/2-4,  room_x/2-1,  room_x/2-1,  room_x/2-1  ]
            ls_y_all = [ -room_y/2+1, -room_y/2+1, -room_y/2+1, -room_y/2+2.5, -room_y/2+4, -room_y/2+5.5, -room_y/2+6, -room_y/2+6, -room_y/2+5, -room_y/2+2.5]
            # ls_x_all = [ -1,  -3,  -5,  -5,    -5,  -5,    -4,  -1,  -1,  -1  ]
            # ls_y_all = [ +1,  +1,  +1,  +2.5,  +4,  +5.5,  +6,  +6,  +5,  +2.5]
            ls_z_all = [0.5, 1.3, 1.5,1.37,1.16,1.23,0.63,1.79,1.83,0.87]

        else:
            ### Get modif file
            modif_csv = PurePath(path_tascar_LINUX, 'session_modif.csv')
            df_modif = pd.read_csv(modif_csv)

            ### Get all modified parameter of the current minute from the df
            df_temp = df_modif[df_modif['minute']==int(minute)]

            t_scattering = df_temp['t_scattering'].iloc[0]
            room_x = df_temp['room_x'].iloc[0]
            room_y = df_temp['room_y'].iloc[0]
            room_z = df_temp['room_z'].iloc[0]
            center_x = df_temp['center_x'].iloc[0]
            center_y = df_temp['center_y'].iloc[0]
            center_z = df_temp['center_z'].iloc[0]
            absorption = df_temp['absorption'].iloc[0]
            damping = df_temp['damping'].iloc[0]
            # t60 = df_temp['t60'].iloc[0]
            ### The csv saves the list as a string so do a work around to get back to a list of floats.
            ### Also position speakers relative to the center of the room
            ls_levels = [float(ls) for ls in (df_temp['ls_levels'].iloc[0][1:-1]).split(",")]
            ls_x_all  = [round(-center_x+float(ls) ,2) for ls in (df_temp['ls_x_all'].iloc[0][1:-1]).split(",")]
            ls_y_all  = [round(-center_y+float(ls) ,2) for ls in (df_temp['ls_y_all'].iloc[0][1:-1]).split(",")]
            ls_z_all  = [float(ls) for ls in (df_temp['ls_z_all'].iloc[0][1:-1]).split(",")]


        ### Determine how many people are talking based on the number of position files
        files_pos_all = list(Path(path_tascar_linux).glob(f'pos*.csv'))
        files_pos_all = [f for f in files_pos_all if f.stem[0]!='.']
        ID_all = [int(files_pos.stem[-1]) for files_pos in files_pos_all]
        ID_talk = ID_all.copy()
        ID_talk.remove(2)
        ID_interf = [3,4,5,6,7]

        ### Load the blocks 
        table = block_table(t_scattering)

        reverb_w, reverb_r = block_reverb(room_x, 
                                          room_y,
                                          room_z, 
                                          center_x, 
                                          center_y, 
                                          center_z,
                                          absorption,
                                          damping,
                                          # t60,
                                          )

        source_id = []
        for idd in ID_interf:
            if idd in ID_talk:
                source_id.append(block_sourceID(idd))
            else:
                source_id.append('')
        source_all = ''.join(source_id)

        noise = block_noise(center_x,
                            center_y,
                            ls_x_all,
                            ls_y_all,
                            ls_z_all,
                            ls_levels,
                            path_spear,
                            session_n,
                            )


        receiver_hoa = block_receiver_hoa()
        receiver_hrtf = block_receiver_hrtf()


        ### Create the scene
        file_scene = PurePath(path_blocks, f'SPEAR_template.tsc')
        file_scene_gui = PurePath(path_blocks, f'SPEAR_template_gui.tsc')

        fin = open(file_scene)
        temp_scene = fin.read()
        fin.close()
        fin = open(file_scene_gui)
        temp_scene_gui = fin.read()
        fin.close()

        scene = temp_scene.format(source_all = source_all,
                                  source_id3 = source_id[0],
                                  source_id4 = source_id[1],
                                  source_id5 = source_id[2],
                                  source_id6 = source_id[3],
                                  source_id7 = source_id[4],
                                  noise    = noise,
                                  table    = table,
                                  room     = reverb_w,
                                  reverb   = reverb_r,
                                  receiver = receiver_hoa,
                                  )
    
        scene_gui = temp_scene_gui.format(source_all = source_all,
                                  source_idX = source_all, # change here for other IDX
                                  noise    = noise,
                                  table    = table,
                                  room     = reverb_w,
                                  reverb   = reverb_r,
                                  receiver = receiver_hrtf,
                                  center_x = str(center_x),
                                  center_y = str(center_y),
                                  center_z = str(center_z),
                                  )    
    
        ### CREATE TASCAR SCENE FILE
        file_output = PurePath(path_tascar_linux, 'Tascar_scenes.tsc')
        file_output_hrtf = PurePath(path_tascar_linux, 'Tascar_scenes_gui.tsc')

        if os.path.exists(file_output):
            output = open(file_output, 'w')
        else:
            output = open(file_output, 'x')
        output.write(scene)
        output.close()

        if os.path.exists(file_output_hrtf):
            output = open(file_output_hrtf, 'w')
        else:
            output = open(file_output_hrtf, 'x')
        output.write(scene_gui)
        output.close()





### Verification that the output files are exactly 60s long
def tascar_60s_check(file_path):
    sig, fs = sf.read(file_path)
    sf.write(file_path, sig[:fs_out*60,:], fs, subtype='PCM_32')



###### Main fct to run all the scenes of the created tascar file. Separated because it will be run on Linux
def SPEAR_tascarSceneRun(dataset_n, session_n, path_spear, minute_random=False, fmatconv=True):

    if dataset_n==1: raise Exception('Dataset 1 do not have Tascar simulations.')

    path_fmatconv = PathFinder(0, 0, 'hoa', path_spear=path_spear)
    path_fmatconv = list(Path(path_fmatconv).glob(f'fmat*.conf'))
    if len(path_fmatconv)!=1:
        path_fmatconv = [f for f in path_fmatconv if f.stem[0]!='.']
    path_fmatconv = path_fmatconv[0]

    ### List of minute of current dataset
    path_tascar_LINUX = PathFinder(dataset_n, session_n, option, path_spear=path_spear)
    path_walk = [Path(x[0]) for x in os.walk(str(path_tascar_LINUX))]
    path_walk.pop(0)
    path_walk.sort()
    minutes = [walk.stem for walk in path_walk]

    ### Path for the output array signals
    path_array_LINUX = PathFinder(dataset_n, session_n, 'array', path_spear=path_spear)
    path_ref_LINUX   = PathFinder(dataset_n, session_n, 'reference', path_spear=path_spear)

    if minute_random:
        minute_n = random.randrange(len(minutes))
        minutes = minutes[minute_n:minute_n+1]

    for minute in minutes:
        ### Working path for the current minute and the current scene in tascar, ref and array
        path_ref_linux    = PurePath(path_ref_LINUX,    minute)
        path_tascar_linux = PurePath(path_tascar_LINUX, minute)
        file_output = PurePath(path_tascar_linux, 'Tascar_scenes.tsc')

        ### Determine how many people are talking based on the number of position files
        files_pos_all = list(Path(path_tascar_linux).glob(f'pos*.csv'))
        files_pos_all = [f for f in files_pos_all if f.stem[0]!='.']
        ID_all = [int(files_pos.stem[-1]) for files_pos in files_pos_all]
        ID_talk = ID_all.copy()
        ID_talk.remove(2)


        ### Scenes parameters
        sounds_all    = ['full',                 'ref'  ]
        sources_all   = [['All', 'Ls', 'ID'],    ['ID'] ]
        ID_scenes_all = [[[''],  [''], ID_talk], [ID_talk]]

        ### Choose output folder. Now all in ref
        path_out =  path_ref_linux

        ### Run Tascar for all scenes
        # jackd -d coreaudio -r 48000 -p 64 -m 
        # jackd -d alsa -r 48000 -p 256 -m 
        for sound, sources, ID_scenes in zip(sounds_all, sources_all, ID_scenes_all):
            for source, ID_scene in zip(sources, ID_scenes):
                for idd in ID_scene:

                    ### Get the array signal from the HOA (get the name and check if it exists)
                    array_name = f'array_{sound}_{source}{idd}'
                    array_file = PurePath(path_out, f'{array_name}.wav')
                    if os.path.exists(array_file):
                        print(f'Array file {array_name} for D{dataset_n} S{session_n} M{minute} already exists, skipped.')
                        continue

                    ### Run the scene and get the HOA
                    scene_name =        f'Scene_{sound}_source{source}{idd}'
                    HOA_name = f'HOA{hoa_order}_{sound}_source{source}{idd}'
                    if platform.system()=='Linux':
                        HOA_file = tempfile.NamedTemporaryFile(prefix=f'{HOA_name}_', suffix='.wav',dir='/dev/shm',delete=False)
                    elif platform.system()=='Darwin':
                        HOA_file = PurePath(path_tascar_linux, f'{HOA_name}.wav')
                    print(f'Running {HOA_name} for D{dataset_n} S{session_n} M{minute}')
                    os.system(f"export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH\ntascar_renderfile   --fragsize 256 --scene {scene_name} -o {HOA_file.name} -r {fs_out} {file_output}")

                    # small delay as sometimes the output file cannot be opened
                    time.sleep(0.1)
                    
                    ### Get the array signal from the HOA (run the convolution)
                    if fmatconv:
                        print(f'Running fmatconvol for D{dataset_n} S{session_n} M{minute}')
                        os.system(f"fmatconvol {path_fmatconv} {HOA_file.name} {array_file}")                            
                        tascar_60s_check(array_file)
                        print(f'Success, now deleting HOA file D{dataset_n} S{session_n} M{minute}')
                        os.system(f'rm {HOA_file.name}')
                    else:
                        print('fmatconvolve currently disabled ')
                        continue                               

                    ### With the create array signal, just extract channel 5 and 6 for binaural ref
                    if sound == 'ref':
                        ref_file = PurePath(path_out, f'ref_D{dataset_n}_S{session_n}_M{minute}_ID{idd}.wav')
                        s_arr, fs_arr = sf.read(array_file)
                        sf.write(ref_file, s_arr[:fs_out*60,4:], fs_arr, subtype='PCM_32')



### Tascar generation of Array Audio and Ref Audio
if __name__ == '__main__':

    ### Choose dataset and session to run
    dataset_n = 2
    session_n = 1

    ### Provide path to the SPEAR directory
    path_spear = '/SPEAR-dir'

    ### Generate tascar file
    random.seed(42) # makes time variations of talkers repeatable
    SPEAR_tascarSceneGen(dataset_n, session_n, path_spear)

    ### Run tascar file and generate audio
    SPEAR_tascarSceneRun(dataset_n, session_n, path_spear, minute_random=False, fmatconv=False)