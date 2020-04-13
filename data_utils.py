import subprocess
import logging

import json
import urllib.request, json 
import urllib
#from urlparse import urlparse
from os.path import splitext

import logging 
import os.path


process = subprocess.Popen(['echo', 'More output'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
stdout, stderr



from datetime import datetime

timestamp = 1545730073
dt_object = datetime.fromtimestamp(timestamp)

def create_wav_list_file(wav_file_path,wav_list_path):
    """

    appends to wav_list file each new data row

    """

    append_row_file(wav_list_path,wav_file_path)



def append_row_file(file,row):
    """

    appends data row to a text file

    """

    with open(file, "a") as myfile:
        myfile.write(row)


def check_if_file_exists(filepath):
    
    return os.path.isfile(filepath)


def write_json_to_file(json_object,filepath):
    import json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_object, f, ensure_ascii=False, indent=4)


def download_transcriptions(final_text_url,destination_transcription_file):
    try:
        #downloaded_audio_count=downloaded_audio_count + 1

        #urllib.urlretrieve(final_text_url, destination_directory + "transcriptions.json")
        transcription_exists=check_if_file_exists(destination_transcription_file)
        if transcription_exists:
            print("transcriptions.txt already exists not downloading")
            return 

        # download audio data and parse it as json
        print("downloading transcriptions json")
        with urllib.request.urlopen(final_text_url) as url:
            #data = json.loads(url.read().decode())
            transcription_json = json.loads(url.read().decode())
        #print(data)


        transcription_json=transcription_json["data"]
        #create_wav_list_file(url)
        for sentence in transcription_json:
            sentence_id=sentence["id"]
            sentence_transcript=sentence["sentence"]
            
            # check if sentence is empty
            if sentence_transcript=="":
                empty_transcript_counter=empty_transcript_counter + 1
            
            else:
                # write the sentence to transcription file
                transcription_row=str(sentence_id) + " " + str(sentence_transcript) + "\n"
                append_row_file(destination_transcription_file,transcription_row)


    except Exception as ex:
        print(ex)
        logging.error(logging.traceback.format_exc())


    

def filter_epoch(data_epoch,minimum_epoch,maximum_epoch):
    """ 
    this function takes current epoch id for current row in dataset
    minimum epoch and maximum epoch, and checks if current epoch
    is between minimum and maximum epochs if so returns True
    """

    if data_epoch >= minimum_epoch and data_epoch <= maximum_epoch:
        return True
    else:
        return False
        
def convert_mp3_to_wav(mp3_path,output_wav_dir):


        #/usr/bin/ffmpeg -i mp3_dir/$file wav_dir/${out_file}_tmp.wav; 
        #sox wav_dir/${out_file}_tmp.wav -c1 -r16000 -b16 wav_dir/${out_file}.wav ;

    out_file_temp="temp"
    out_file="out"
    process = subprocess.Popen(['/usr/bin/ffmpeg', '-i', mp3_path , output_wav_dir + out_file]
                     ,stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout, stderr

    process2 = subprocess.Popen(['sox', output_wav_dir + out_file_temp , '-c1' , '-r16000' , '-b16',output_wav_dir + out_file]
                     ,stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    stdout2, stderr2 = process.communicate()
    stdout2, stderr2


def read_json_from_file(filepath):
    import json

    with open(filepath, 'r') as f:
        return json.load(f)

def download_audio_json(final_audio_url,destination_audio_file,audio_json_path=""):

    # check if file already exists
    audio_exists=check_if_file_exists(destination_audio_file)
    if not audio_exists:

    
        with urllib.request.urlopen(final_audio_url) as url:
            data = json.loads(url.read().decode())
            print("downloading audio json")

            write_json_to_file(data,destination_audio_file)

            print("writing audio json")
            return data


    else:
        print("audio json already exists skippings")
        return read_json_from_file(audio_json_path)



def append_row_file(file,row):
    """

    appends data row to a text file

    """

    with open(file, "a") as myfile:
        myfile.write(row)
              
def create_wav_list_file(wav_file_path):
    """

    appends to wav_list file each new data row

    """

    append_row_file(wav_list_path,wav_file_path)





def download_single_file(url,downloaded_audio_count,destination_directory):
    try:
        print("downloading single audio file")
        global downloaded_audio_count
        downloaded_audio_count=downloaded_audio_count + 1
        urllib.request.urlretrieve(url, destination_directory + url)
        create_wav_list_file(url)

    except Exception as ex:
        print(ex)
        logging.error(logging.traceback.format_exc())

def download_audio_list(audio_list, destination_directory ):
    """
        input : a list of urls storing audio files
        output : if no error return true, else return -1
    """

    for url in audio_list:
        file_name=url.split("/")[-1]

        urllib.request.urlretrieve(url, destination_directory + file_name)
