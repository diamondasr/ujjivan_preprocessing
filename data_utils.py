
# to do

# mp3 to wav conversion code to download_single_file, so that it doesnt write files that failed
# conversion to wav.scp file




import subprocess
import logging

import json
import urllib.request, json 
import urllib
#from urlparse import urlparse
from os.path import splitext

import logging 
import os.path
wav_list_path="./wav.list"
wav_scp_path="kaldi_outputs/wav.scp"
text_filepath="kaldi_outputs/text"
transcription_filepath="./transcriptions.txt"
destination_wav_directory="./wavs/"


process = subprocess.Popen(['echo', 'More output'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
stdout, stderr

#Create and configure logger 
logging.basicConfig(filename="./script.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w')
#Creating an object 
logger=logging.getLogger() 
  
#Setting the threshold of logger to DEBUG 
logger.setLevel(logging.DEBUG) 

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def generic_shell(shell_command,log_file_name):
    """
        this defines a python function which can run any shell script command
        from python and route logs to log file 
    """

    #print(shell_command.split())
    process = subprocess.Popen(shell_command,
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE,shell=True)
    stdout, stderr = process.communicate()
    stdout, stderr

    

    logging.error("stdout")
    logger = setup_logger('shell_logger', log_file_name)
    logger.info(stdout)

    logging.error("stderror")
    logger = setup_logger('shell_logger', log_file_name)
    logger.info(stderr)

    if (stderr):
        print("exception has occurred, please refer to log file " + log_file_name)



from datetime import datetime

timestamp = 1545730073
dt_object = datetime.fromtimestamp(timestamp)

def read_transcription(transcription_id,transcription_filepath):
    #with open(transcription_filepath, encoding='utf-8') as f:
        #transcripts=f.read()
    
    import csv
    transcription_id=transcription_id.replace(".wav","")
    with open(transcription_filepath) as inf:
        reader = csv.reader(inf, delimiter=" ")
        for row in reader:
            if row[0]==transcription_id:
                return ' '.join(row[1:])

    
    return ""

def append_row_file(file,row):
    """

    appends data row to a text file

    """

    with open(file, "a") as myfile:
        myfile.write(row + "\n")
        
def create_wav_list_file(wav_file_path,wav_list_path="./wav.list"):
    """

    appends to wav_list file each new data row
    also appends to wav.scp file

    """



    append_row_file(wav_list_path,wav_file_path)
    append_row_file(wav_scp_path,wav_file_path.split("/")[-1] + " " + wav_file_path)


def create_text_file(wav_file_path,text_file_path):
    """

    appends to text file 
    

    """

    sentence_id=wav_file_path.split("/")[-1].split("_")[2]
    print("sentence id")
    print(sentence_id)
    transcription=read_transcription(sentence_id,transcription_filepath)
    print("transcription")
    print(transcription)
    text_line=wav_file_path.split("/")[-1] + " " +  transcription

    append_row_file(text_file_path,text_line)



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

    """

    returns True if conversion was successfull , else returns False
    if destination file already exists, by default it replaces it -y flag

    """
    #/usr/bin/ffmpeg -i mp3_dir/$file wav_dir/${out_file}_tmp.wav; 
    #sox wav_dir/${out_file}_tmp.wav -c1 -r16000 -b16 wav_dir/${out_file}.wav ;


    print("converting file " + mp3_path )
    out_file_temp=  mp3_path.split("/")[-1].replace(".mp3",".temp.wav")
    out_file=  mp3_path.split("/")[-1].replace(".mp3",".wav")

    process = subprocess.Popen(['/usr/bin/ffmpeg' ,'-y','-i', mp3_path , output_wav_dir + out_file_temp]
                     ,stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    #print(stdout, stderr)

    if stderr:
        print("error during ffmpeg ")
        logging.error(stdout)
        logging.error(stderr)

    process2 = subprocess.Popen(['sox', output_wav_dir + out_file_temp , '-c1' , '-r16000' , '-b16',output_wav_dir + out_file]
                     ,stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    stdout2, stderr2 = process2.communicate()
    #print(stdout2, stderr2)

    if stderr2:
        print("error during sox ")
        logging.error(stdout)
        logging.error(stderr)


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










def download_single_file(url,downloaded_audio_count,destination_directory):
    """
    downloads mp3 file
    updates wav.list file
    updates wav.scp file
    updates kaldi_outputs/text file
    """
    try:
        print("downloading single audio file")
        #global downloaded_audio_count
        
        destination_filename= url.split("/")[-1]
        destination_path=destination_directory + destination_filename
        urllib.request.urlretrieve(url, destination_path)
        
 
        output_wav_filename= url.split("/")[-1].replace("mp3","wav")
        output_destination_path=destination_wav_directory + output_wav_filename
        convert_mp3_to_wav(destination_path,destination_wav_directory  )
        create_wav_list_file(output_destination_path)
        downloaded_audio_count=downloaded_audio_count + 1

        create_text_file(output_destination_path, text_filepath)



        return destination_path

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
