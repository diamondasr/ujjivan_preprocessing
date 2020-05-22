# generic file utility functions

import os
from shell_utils import generic_shell
#from kaldi_utils import create_wav_list_file,create_text_file
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

def remove_duplicate_lines(input_file,output_file):
    """
    removes duplicate lines from a text file
    """

    lines_seen = set() # holds lines already seen
    outfile = open(output_file, "w")
    for line in open(input_file, "r"):
        if line not in lines_seen: # not a duplicate
            outfile.write(line)
            lines_seen.add(line)
    outfile.close()

def create_dir(dir_path,language_code):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)