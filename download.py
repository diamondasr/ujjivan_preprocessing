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
destination_wav_dir
# Create the parser
argument_parser = argparse.ArgumentParser(description='Parser for preprocessing script for Ujjivan')

# Add the arguments
argument_parser.add_argument('-lang',
                       type=str,
                       help='the lang id which is used is url of azure for example ta')

argument_parser.add_argument('-source_mp3_dir',
                       type=str,
                       help='the source mp3 directory containing audio files')

argument_parser.add_argument('-',
                       type=str,
                       help='the destination directory where wav files are stored')



# Execute the parse_args() method
args = argument_parser.parse_args()




audio_source="https://vca-admin.azurewebsites.net/v1/audio?passcode=N@v4n473ch&language_code="
text_source="https://vca-admin.azurewebsites.net/v1/sentence?passcode=N@v4n473ch&language_code="
language_code=args.lang # this is part of url of audio source and text source

speaker_id="225"  # default value is -1 
extension=".mp3" # default value is -1 

final_audio_url=audio_source + language_code
final_text_url=text_source + language_code

destination_directory="./audios/"
#destination_wav_directory="./wavs/"
#wav_list_path="./wav.list"

destination_transcription_file="data/" + language_code + "/transcriptions.txt"
destination_audio_file="data/" + language_code +"/audio.json"

#epoch_start=-1
#epoch_end=-1
lexicon_language_code="tamil" # this is the language code that we enter in g2p repl.py

#"/home/ubuntu/datasets/trial/voicecollectionblobcontainer/"
source_mp3_directory=args.source_mp3_dir

text_filepath= os.getcwd() + "/kaldi_outputs/text"

downloaded_audio_count=0
#number_of_rows=50 # how many data items do you need in dataset
#empty_transcript_counter=0

wav_scp_path= os.getcwd() + "/kaldi_outputs/wav.scp" # where will wav.scp be stored temporarily
wav_list_path= os.getcwd() + "/wav.list"              # where will wav.list be stored temporarily


#  os.getcwd() + "/wavs/" + language_code + "/"
destination_wav_directory= args.destination_wav_dir + language_code + "/"

spk2utt_filepath= os.getcwd() + "/kaldi_outputs/spk2utt"  # where will spk2utt be stored temporarily
utt2spk_filepath= os.getcwd() + "/kaldi_outputs/utt2spk"  # where will utt2spk be stored temporarily

transcription_filepath= os.getcwd() + "/data/" + language_code + "/transcriptions.txt"


temp_lexicon_path= os.getcwd() + "/lexicon_left" # it only stores each word in each line , this file is just temporary
final_lexicon_path=os.getcwd() + "/data/" + language_code + "/lexicon.txt" # the final lexicon file generated by g2p script, this should be moved to place like kaldi_outputs/ta/ta_15k


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

# create initial kaldi directory structure
create_kaldi_directories(language_code,args.destination_wav_dir,create_subset_split_dirs=False)

# download transcriptions and then creates a list of words and then runs g2p to create final lexicon file
download_transcriptions(final_text_url,destination_transcription_file,temp_lexicon_path,final_lexicon_path, lexicon_language_code,language_code)

# download audio json files
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
                        destination_mp3_path=convert_single_file(row,downloaded_audio_count,destination_directory,speaker_id,source_mp3_directory,destination_wav_directory,text_filepath,spk2utt_filepath,utt2spk_filepath,transcription_filepath,wav_list_path,wav_scp_path,language_code)
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
                        destination_mp3_path=convert_single_file(row,downloaded_audio_count,destination_directory,speaker_id,source_mp3_directory,destination_wav_directory,text_filepath,spk2utt_filepath,utt2spk_filepath,transcription_filepath,wav_list_path,wav_scp_path,language_code)


                        #convert_mp3_to_wav(mp3_path,output_wav_dir)

except Exception as ex:
    print("there was exception in download.py")
    #print(ex)


# create kaldi subdirectory for new split like ta_15k, it can only be done after wav.scp,text,spk2utt have already been generated
create_kaldi_directories(language_code,args.destination_wav_dir,create_subset_split_dirs=True)

# creates train test split
#create_kaldi_subset(wav_scp_path,"kaldi_outputs" , language_code)

# creates kaldi/data/local/dict 
#create_kaldi_lang(language_code)


# removes temp files 
rm_unnecessary_files(language_code)

# close_system
close_system(language_code)

print("Done")
#print("inside kaldi recipie directory")
#print(" ln -s " + os.getcwd() + "/kaldi_outputs/data .")
#print(" ln -s " + os.getcwd() + "/kaldi_outputs/exp .")
#sprint(" ln -s " + os.getcwd() + "/kaldi_outputs/mfcc .")



                    









