
# generic file utility functions

import os
from shell_utils import generic_shell
from kaldi_utils import create_wav_list_file,create_text_file
import logging
import subprocess


def append_row_file(file,row):
    """
    general function which appends data row to a text file
    """
    with open(file, "a") as myfile:
        myfile.write(row + "\n")

def check_if_file_exists(filepath):   
    return os.path.isfile(filepath)

def write_json_to_file(json_object,filepath):
    import json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_object, f, ensure_ascii=False, indent=4)

def read_file_to_list(filepath):
    """
        simple utility function which basically reads input file having one entry in each line
        to a python list 
    """
    if os.path.isfile(filepath): 
        with open(filepath) as f:
            return f.read().splitlines() 
    else:
        return []


def write_list_to_file(my_list,filepath):
    """
    a simple utility function to write a python list to file 
    """
    with open(filepath, mode='wt', encoding='utf-8') as myfile:
        myfile.write('\n'.join(my_list))

def count_lines(file_path):
    with open(file_path) as foo:
        lines = len(foo.readlines())
    return lines



def remove_file(filepath):
    """
        utility function to remove a file but checks if it exists before removing it
    """
    if os.path.isfile(filepath):
        os.remove(filepath)

def sort_file(filepath,language_code):
    base_path=os.path.dirname(filepath)
    base_name=os.path.basename(filepath)
    sorted_file_name=base_path + '/' +  base_name + '_sorted'
    generic_shell("sort " + filepath + " > " + sorted_file_name, "logs/" + language_code + ".sort.log" )
    remove_file(filepath)
    generic_shell('cp ' + sorted_file_name + ' ' + filepath,"logs/" + language_code + ".sort.log")
    remove_file(sorted_file_name)

def convert_mp3_to_wav(mp3_path,output_wav_dir,language_code):
    """
    returns True if conversion was successfull , else returns False
    if destination file already exists, by default it replaces it -y flag
    """
    #/usr/bin/ffmpeg -i mp3_dir/$file wav_dir/${out_file}_tmp.wav; 
    #sox wav_dir/${out_file}_tmp.wav -c1 -r16000 -b16 wav_dir/${out_file}.wav ;

    out_file_temp=  mp3_path.split("/")[-1].replace(".mp3",".temp.wav")
    out_file=  mp3_path.split("/")[-1].replace(".mp3",".wav")

    process = subprocess.Popen(['/usr/bin/ffmpeg' ,'-hide_banner' ,'-nostats', '-y', '-i', mp3_path , output_wav_dir + out_file_temp]
                     ,stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if stderr:
        logging.error(stderr)

    process2 = subprocess.Popen(['sox', output_wav_dir + out_file_temp , '-c1' , '-r16000' , '-b16',output_wav_dir + out_file]
                     ,stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    stdout2, stderr2 = process2.communicate()

    shell_command="rm " + output_wav_dir + out_file_temp 
    generic_shell(shell_command,"logs/" + language_code + "." + "rm.log")

    if stderr2:
        logging.error(stderr2)

def read_json_from_file(filepath):
    import json
    with open(filepath, 'r') as f:
        return json.load(f)

def convert_single_file(url,downloaded_audio_count,destination_directory,speaker_id,source_mp3_directory,destination_wav_directory,text_filepath,spk2utt_filepath,utt2spk_filepath,transcription_filepath,wav_list_file,wav_scp_path,language_code):
    """
    converts mp3 to wav file , updates wav.list , wav.scp text ,spk2utt file
    """
    try:
        destination_filename= url.split("/")[-1]
        destination_path= source_mp3_directory + destination_filename 
        output_wav_filename= url.split("/")[-1].replace("mp3","wav")
        utterance_id=url.split("/")[-1].replace(".mp3","")
        # check if file has already been converted
        output_destination_path=destination_wav_directory + output_wav_filename
        if not utterance_id in  conversion_file_set:
            convert_mp3_to_wav(destination_path,destination_wav_directory ,language_code )
            conversion_file_set.add(utterance_id)
        
        create_wav_list_file(output_destination_path,wav_list_file,wav_scp_path)
        downloaded_audio_count=downloaded_audio_count + 1
        create_text_file(output_destination_path, text_filepath,transcription_filepath)
        append_row_file(spk2utt_filepath, utterance_id + "_" +  str(speaker_id) + " " + utterance_id )
        append_row_file(utt2spk_filepath, utterance_id + " "  +  utterance_id + "_" +  str(speaker_id))

        return destination_path

    except Exception as ex:
        print("exception during convert single file function")
        logging.error(logging.traceback.format_exc())


def read_transcription(transcription_id,transcription_filepath):
    # gets transcription from transcriptions.txt having corresponding id  
    import csv
    transcription_id=transcription_id.replace(".wav","")
    with open(transcription_filepath) as inf:
        reader = csv.reader(inf, delimiter=" ")
        for row in reader:
            if row[0]==transcription_id:
                return ' '.join(row[1:])
    return ""
