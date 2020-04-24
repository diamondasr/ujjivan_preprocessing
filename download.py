"""
# Author Saurabh Vyas , Navanatech

This python3 script downloads audio.json and transcriptions.txt, and creates a folder called wavs and 10 subdirectories,
then for given language it converts all mp3 files according to audio.json to its correspoding subdirectory in wav 



"""
import json
import urllib.request, json 
#import urllib.parses
import os
#from urlparse import urlparse
import argparse
from os.path import splitext
from tqdm import tqdm
import logging 
from data_utils import download_transcriptions, init_system, close_system , create_kaldi_lang,rm_unnecessary_files,create_kaldi_subset,create_kaldi_directories,write_json_to_file,check_if_file_exists,download_audio_json , read_json_from_file , convert_single_file,convert_mp3_to_wav

# Create the parser
argument_parser = argparse.ArgumentParser(description='Parser for preprocessing script for Ujjivan')

# Add the arguments
argument_parser.add_argument('-lang',
                       type=str,
                       help='the lang id which is used is url of azure for example ta')



# Execute the parse_args() method
args = argument_parser.parse_args()


#from data_utils import *          
  
#Create and configure logger 
logging.basicConfig(filename="logs/main.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w')
#Creating an object 
logger=logging.getLogger() 
  
#Setting the threshold of logger to DEBUG 
logger.setLevel(logging.DEBUG) 

audio_source="https://vca-admin.azurewebsites.net/v1/audio?passcode=N@v4n473ch&language_code="
text_source="https://vca-admin.azurewebsites.net/v1/sentence?passcode=N@v4n473ch&language_code="
language_code=args.lang 
speaker_id="225"  # default value is -1 
extension=".mp3" # default value is -1 
final_audio_url=audio_source + language_code
final_text_url=text_source + language_code

destination_directory="./audios/"
#destination_wav_directory="./wavs/"
wav_list_path="./wav.list"
destination_transcription_file="data/" + language_code + "/transcriptions.txt"
destination_audio_file="data/" + language_code +"/audio.json"

epoch_start=-1
epoch_end=-1

source_mp3_directory="/home/ubuntu/datasets/trial/voicecollectionblobcontainer/"

downloaded_audio_count=0
number_of_rows=50 # how many data items do you need in dataset
empty_transcript_counter=0

wav_scp_path= os.getcwd() + "/kaldi_outputs/wav.scp"


def get_ext(url):
    """Return the filename extension from url, or ''."""
    parsed = urllib.parse.urlparse(url)
    root, ext = splitext(parsed.path)
    return ext  # or ext[1:] if you don't want the leading '.'



def check_file_extension(row,extension):
    """
        If current row has incorrect extension return False else return True
    """
    file_extension=get_ext(row)
    #print(file_extension)
    if extension != -1:
        if file_extension == extension:
            return True
        else:
            return False
    else:
        return False

# initialize system
init_system(language_code)

# create kaldi directory structure
create_kaldi_directories(language_code)

# download transcriptions
download_transcriptions(final_text_url,destination_transcription_file)

# download audio json
data=download_audio_json(final_audio_url,destination_audio_file)


data=data["data"]
# see if specific speaker id is provided

    

try:
    if speaker_id != -1:
        print("filtering according to specific speaker")
        data=data[speaker_id]
        #print(data)
        #print(data)
        for row in tqdm(data):
            #print(row)
            extension_valid=check_file_extension(row,extension)
            #print(extension_valid)

            if extension_valid:
                        #print("valid extension")
                        # download audio
                        #print("downloading audio for row")
                        #download_single_file(row)
                        destination_mp3_path=convert_single_file(row,downloaded_audio_count,destination_directory,speaker_id,source_mp3_directory)
                        #basename=destination_mp3_path.split("/")[-1]
                        
                    
                    #convert_mp3_to_wav(destination_mp3_path,destination_wav_directory  )

    else:
        print("speaker filtering disabled ")
        for speaker_id in data:
            print(speaker_id)
            for row in data[speaker_id]:
                print(row)
                #print(data[speaker_id])
                extension_valid=check_file_extension(row,extension)
                if extension_valid:
                    
                        # download audio
                        destination_mp3_path=convert_single_file(row,downloaded_audio_count,destination_directory,speaker_id,source_mp3_directory)


                        #convert_mp3_to_wav(mp3_path,output_wav_dir)

except Exception as ex:
    print("there was exception in download.py")
    #print(ex)


# create kaldi subdirectory for new split like ta_15k, it can only be done after wav.scp,text,spk2utt have already been generated
create_kaldi_directories(language_code,create_subset_split_dirs=True)

# creates train test split
#create_kaldi_subset(wav_scp_path,"kaldi_outputs")

# creates kaldi/data/local/dict 
#create_kaldi_lang()


rm_unnecessary_files()

# close_system
close_system(language_code)

print("Done")
#print("inside kaldi recipie directory")
#print(" ln -s " + os.getcwd() + "/kaldi_outputs/data .")
#print(" ln -s " + os.getcwd() + "/kaldi_outputs/exp .")
#sprint(" ln -s " + os.getcwd() + "/kaldi_outputs/mfcc .")



                    









