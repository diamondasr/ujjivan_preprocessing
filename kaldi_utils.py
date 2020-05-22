# utility functions that involve kaldi

import os
from file_utils import remove_file , sort_file,count_lines,read_file_to_list,append_row_file, read_transcription, create_dir
from shell_utils import generic_shell

def rm_unnecessary_files(language_code,dir_prefix):
    """ this functions deletes some temporary files , for example before train/test split and also sorts files """

    files_to_remove=['lexicon_left','lexicon.txt','wav.list','test_ids','dataset_ids','train_ids','kaldi_outputs/wav.scp','kaldi_outputs/text','kaldi_outputs/lexicon.txt','kaldi_outputs/spk2utt','kaldi_outputs/utt2spk','lexion_temp2','lexicon_temp3']
    for file in files_to_remove:
        remove_file(file)

    basepath='kaldi_outputs/' + language_code + "/" + dir_prefix + "/"
    files_to_sort=[ basepath + 'wav.scp', basepath + 'spk2utt', basepath + 'utt2spk', basepath + 'text' ]
    for file in files_to_sort:
        sort_file(file,language_code)

def create_split_dir(language_code,wav_scp_count):
    """
        Create a new dir in kaldi_outputs/lang_id/lang_wav_scp_count
        for eg. kaldi_outputs/ta/ta_15200
    """

    print("split directory doesnt exist, creating ..")
    create_dir("kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count,language_code)
    cp_source=['kaldi_outputs/wav.scp','kaldi_outputs/text','kaldi_outputs/spk2utt','kaldi_outputs/utt2spk','data/' + language_code +  '/lexicon.txt']
    for source in cp_source:
        generic_shell("cp " + source + " kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count, "logs/" + language_code + "." + 'cp.log')


def create_kaldi_directories(language_code,destination_wav_dir,create_subset_split_dirs=False):
    """ this function generates folder structure which kaldi expects, also creates some general directories not for kaldi
        for example it creates kaldi_outputs/<lang_code>/<split>/
    """
    wav_scp_count=0
    mkdir_dirs=["logs","data", "data/" + language_code , "kaldi_outputs" , "kaldi_outputs/" + language_code,destination_wav_dir,destination_wav_dir + language_code]
    for dir in mkdir_dirs:
        os.makedirs(dir,exist_ok=True)
        
    if create_subset_split_dirs==True:
        if not os.path.isfile("kaldi_outputs/" +   "wav.scp"):
            # this means all files were already processed so there is no new file
            print("not creating new split since no new file present")
            return
        
        # read the length of wav.scp in kaldi_outputs/language_id
        wav_scp_count=str(count_lines("kaldi_outputs/"  + "wav.scp"))

        # check if wav_scp_count is present in file called .subsets.txt in kaldi_outputs/language_id
        # if yes skip , dont do anything, if not create a subdirectory in kaldi_outputs/language_id called language_id_wav_scp_count
        
        if os.path.isfile("kaldi_outputs/" +  language_code + "/.subsets.txt"):
            print ("subset file exists for language")
            print("wav scp count : " + str(wav_scp_count))
            subset_counts=read_file_to_list("kaldi_outputs/" +  language_code + "/.subsets.txt")
            
            if wav_scp_count in subset_counts:
                print("split directory already existing")
            else:
                create_split_dir(language_code,wav_scp_count)        
        else:
            print ("subsets.txt doesnt exist creating it for the first time")
            append_row_file("kaldi_outputs/" +  language_code + "/.subsets.txt",wav_scp_count)
            create_split_dir(language_code,wav_scp_count)

    return language_code + "_" + str(wav_scp_count) # this will be used by other functions later, to store files in this subset

def create_kaldi_wav_scp_file(wav_file_path,wav_list_path,wav_scp_path):
    """
    appends audio file path to wav_list file each new data row
    also appends to wav.scp file
    """
    utterance_id=wav_file_path.split("/")[-1].replace(".wav","")
    append_row_file(wav_list_path,wav_file_path)
    append_row_file(wav_scp_path,utterance_id + " " + wav_file_path)

def create_kaldi_text_file(wav_file_path,text_file_path,transcription_filepath):
    """
    appends to kaldi text ( data/text in usual kaldi directory ) file 
    """
    sentence_id=wav_file_path.split("_")[2].split('.')[0]
    transcription=read_transcription(sentence_id,transcription_filepath)
    text_line=wav_file_path.split("/")[-1].replace(".wav","") + " " +  transcription
    append_row_file(text_file_path,text_line)

