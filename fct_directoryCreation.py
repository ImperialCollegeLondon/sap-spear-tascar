"""
SPEAR Challenge

Create the directory of the Challenge for Train, Dev and Eval set.

Needs as input the path to the EasyComDataset to know the number of minutes per session.
cf: path_corpora

"""


from pathlib import Path
from pathlib import PurePath
import os


### Function to make us able to deal only with PurePosixPath type data
def my_mkdir(path_folder):
    path_folder = str(path_folder)
    if not os.path.exists(path_folder):
        os.system("mkdir '" + path_folder + "'")


def SPEAR_directory_creation(path_spear_root, path_corpora):
    name_spear = 'SPEAR'
    path_spear  = PurePath(path_spear_root, name_spear)
    my_mkdir(path_spear)

    ### Create top directories
    dir_main  = 'Main'
    dir_extra = 'Extra'

    Path_main  = PurePath(path_spear, dir_main)
    Path_extra = PurePath(path_spear, dir_extra)

    my_mkdir(Path_main)
    my_mkdir(Path_extra)

    ### Take a folder from EasyCom to count the sessions and get the minutes
    Path_minute  = Path(PurePath(path_corpora, 'EasyComDataset', 'Main', 'Speech_Transcriptions'))
    Path_minutes = list(Path_minute.glob('**/*.json'))
    Path_minutes = [f for f in Path_minutes if f.stem[0]!='.']
    Path_minutes.sort()


    for Path_file in Path_minutes:
        name_session = Path_file.parts[-2]
        name_minute  = Path_file.parts[-1][0:2]

        ### InitialRelease: Train/Dev split with first 9 sessions in Train and 10,11,12 in Dev
        if any([sess in name_session for sess in ['10', '11', '12']]):
            name_set = 'Dev'
        elif any([sess in name_session for sess in ['13', '14', '15']]):
            name_set = 'Eval'
        else:
            name_set = 'Train'

        Path_extra_set = PurePath(Path_extra, name_set)
        my_mkdir(Path_extra_set)
        Path_main_set  = PurePath(Path_main, name_set)
        my_mkdir(Path_main_set)


        N_dataset = 4
        for n_dataset in range(1,N_dataset+1):

            ### Create current Dataset directory
            name_dataset = f'Dataset_{n_dataset}'

            ###### EXTRA
            Path_dataset = PurePath(Path_extra_set, name_dataset)
            my_mkdir(Path_dataset)

            ### Create VAD directory with all sessions in current dataset
            name_VAD         = 'VAD'
            Path_VAD         = PurePath(Path_dataset, name_VAD)
            Path_VAD_session = PurePath(Path_VAD, name_session)
            my_mkdir(Path_VAD)
            my_mkdir(Path_VAD_session)

            ### Reference_Audio
            name_ref         = 'Reference_Audio'
            Path_ref         = PurePath(Path_dataset, name_ref)
            Path_ref_session = PurePath(Path_ref, name_session)
            Path_ref_minutes = PurePath(Path_ref_session, name_minute)
            my_mkdir(Path_ref)
            my_mkdir(Path_ref_session)
            my_mkdir(Path_ref_minutes)

            ### Create TASCAR directory with all sessions for all minutes in current dataset (not in 1)
            if n_dataset !=1:
                name_tascar         = 'TASCAR'
                Path_tascar         = PurePath(Path_dataset, name_tascar)
                Path_tascar_session = PurePath(Path_tascar, name_session)
                Path_tascar_minutes = PurePath(Path_tascar_session, name_minute)
                my_mkdir(Path_tascar)
                my_mkdir(Path_tascar_session)
                my_mkdir(Path_tascar_minutes)

            ### Reference_PosOri
            name_ref2         = 'Reference_PosOri'
            Path_ref2         = PurePath(Path_dataset, name_ref2)
            Path_ref2_session = PurePath(Path_ref2, name_session)
            Path_ref2_minutes = PurePath(Path_ref2_session, name_minute)
            my_mkdir(Path_ref2)
            my_mkdir(Path_ref2_session)
            my_mkdir(Path_ref2_minutes)


            ###### MAIN
            Path_dataset = PurePath(Path_main_set, name_dataset)
            my_mkdir(Path_dataset)

            ### Microphone_Array_Audio
            name_array         = 'Microphone_Array_Audio'
            Path_array         = PurePath(Path_dataset, name_array)
            Path_array_session = PurePath(Path_array, name_session)
            my_mkdir(Path_array)
            my_mkdir(Path_array_session)


            ### Array_Orientation
            name_ori         = 'Array_Orientation'
            Path_ori         = PurePath(Path_dataset, name_ori)
            Path_ori_session = PurePath(Path_ori, name_session)
            my_mkdir(Path_ori)
            my_mkdir(Path_ori_session)

            ### DOA_sources
            name_DOA         = 'DOA_sources'
            Path_DOA         = PurePath(Path_dataset, name_DOA)
            Path_DOA_session = PurePath(Path_DOA, name_session)
            my_mkdir(Path_DOA)
            my_mkdir(Path_DOA_session)



    ### Miscellaneous folder for ambient noise and Tascar hoa 15 info
    dir_misc = 'Miscellaneous'
    Path_misc = PurePath(path_spear, dir_misc)
    my_mkdir(Path_misc)

    ### Additional ambient noise
    name_noise   = 'AmbientNoise'
    Path_noise = PurePath(Path_misc, name_noise)
    my_mkdir(Path_noise)

    ### Additional hoa conv weights
    name_hoa   = 'HOA_weights'
    Path_hoa = PurePath(Path_misc, name_hoa)
    my_mkdir(Path_hoa)

    ### Additional ATF
    name_atf   = 'Array_Transfer_Functions'
    Path_atf = PurePath(Path_misc, name_atf)
    my_mkdir(Path_atf)

if __name__ == '__main__':
    ### Top Path to modify to create new datasets
    path_source  = str(Path(os.path.realpath(__file__)).parents[1])
    path_corpora = PurePath(path_source, 'corpora')

    SPEAR_directory_creation(path_source, path_corpora)
