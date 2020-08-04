"""
# Author Saurabh Vyas , Navanatech

This is python3 script which preprocesses ujjivan data

"""

import json
import urllib.request
import os
import argparse
from os.path import splitext
from tqdm import tqdm
import logging 

from data_utils import create_kaldi_directories , init_system ,download_transcriptions
from data_utils import  download_audio_json , convert_single_file ,close_system

from kaldi_utils import rm_unnecessary_files

# Create the parser
argument_parser = argparse.ArgumentParser(description='Parser for preprocessing script for Ujjivan')

# Add the arguments
argument_parser.add_argument('-lang',
                       type=str,
                       help='the lang id which is used is url of azure for example ta', required=True)

argument_parser.add_argument('-source_mp3_dir',
                       type=str,
                       help='the source mp3 directory containing audio files', required=True)

argument_parser.add_argument('-destination_wav_dir',
                       type=str,
                       help='the destination directory where wav files are stored', required=True)

argument_parser.add_argument('-automatic_lexicon_generation',
                       type=str,
                       help='should it automatically generate lexicon , true or false', required=True)


argument_parser.add_argument('-custom_transcription',
                       type=str,
                       help='do you want to use your own transcriptions file ?')

argument_parser.add_argument('-custom_transcription_path',
                       type=str,
                       help='path for custom transcription file')

argument_parser.add_argument('-transliteration_map_file_path',
                       type=str,
                       help='path for transcription mapping file')

args = argument_parser.parse_args()
language_code=args.lang # this is part of url of audio source and text source
source_mp3_directory=args.source_mp3_dir
if source_mp3_directory[-1] != '/':
    source_mp3_directory=source_mp3_directory + '/'


audio_source="https://vca-admin.azurewebsites.net/v1/audio?passcode=N@v4n473ch&language_code="
text_source="https://vca-admin.azurewebsites.net/v1/sentence?passcode=N@v4n473ch&language_code="
final_audio_url=audio_source + language_code
final_text_url=text_source + language_code

speaker_id=-1  # default value is -1 
extension=".mp3" # default value is -1 
downloaded_audio_count=0
row_count=0

if args.destination_wav_dir[-1] != '/':
    args.destination_wav_dir=args.destination_wav_dir + '/'
destination_wav_directory= args.destination_wav_dir + language_code + "/"
wav_list_path= os.getcwd() + "/wav.list"              # where will wav.list be stored temporarily

destination_directory="./audios/"
destination_audio_file="data/" + language_code +"/audio.json"

destination_transcription_file="data/" + language_code + "/transcriptions.txt"
transcription_filepath= os.getcwd() + "/data/" + language_code + "/transcriptions.txt"
custom_transcription=args.custom_transcription
custom_transcription_file_path=args.custom_transcription_path


temp_lexicon_path= os.getcwd() + "/lexicon_left" # it only stores each word in each line , this file is just temporary
final_lexicon_path=os.getcwd() + "/data/" + language_code + "/lexicon.txt" # the final lexicon file generated by g2p script, this should be moved to place like preprocessed_outputs/ta/ta_15k

text_filepath= os.getcwd() + "/preprocessed_outputs/text"
wav_scp_path= os.getcwd() + "/preprocessed_outputs/wav.scp" # where will wav.scp be stored temporarily
spk2utt_filepath= os.getcwd() + "/preprocessed_outputs/spk2utt"  # where will spk2utt be stored temporarily
utt2spk_filepath= os.getcwd() + "/preprocessed_outputs/utt2spk"  # where will utt2spk be stored temporarily


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

# create initial kaldi directory structure
create_kaldi_directories(language_code,args.destination_wav_dir,create_subset_split_dirs=False)

# initialize system
init_system(language_code)

# download transcriptions json and then creates a list of words and then runs g2p to create final lexicon file
download_transcriptions(final_text_url,destination_transcription_file,temp_lexicon_path,\
final_lexicon_path,language_code, args.transliteration_map_file_path ,args.automatic_lexicon_generation,\
    custom_transcription_file_path,custom_transcription)

# download audio json file
audio_json=download_audio_json(final_audio_url,destination_audio_file)

audio_json=audio_json["data"]
# see if specific speaker id is provided

try:
    if speaker_id != -1:
        print("filtering according to specific speaker")
        speaker_rows=audio_json[speaker_id]
        for row in tqdm(speaker_rows):
            row_count=row_count + 1
            extension_valid=check_file_extension(row,extension)
            if extension_valid:
                        destination_mp3_path=convert_single_file(row,downloaded_audio_count,destination_directory,speaker_id,\
                        source_mp3_directory,destination_wav_directory,text_filepath,spk2utt_filepath,utt2spk_filepath,\
                        transcription_filepath,wav_list_path,wav_scp_path,language_code)
    else:
        print("speaker filtering disabled ")
        for speaker_id in audio_json:
            #print(speaker_id)
            for row in tqdm(audio_json[speaker_id]):
                row_count=row_count + 1
                extension_valid=check_file_extension(row,extension)
                if extension_valid:
                        # download audio
                        destination_mp3_path=convert_single_file(row,downloaded_audio_count,destination_directory,speaker_id, \
                        source_mp3_directory,destination_wav_directory,text_filepath,spk2utt_filepath,utt2spk_filepath,\
                        transcription_filepath,wav_list_path,wav_scp_path,language_code)

except Exception as ex:
    print("there was exception in download.py")

print("total number of rows processed : " + str(row_count))

# create kaldi subdirectory for new split like ta_15k, it can only be done after wav.scp,text,spk2utt have already been generated
# dir_suffix is something like ta_15k
dir_suffix=create_kaldi_directories(language_code,args.destination_wav_dir,create_subset_split_dirs=True)

# removes temp files 
rm_unnecessary_files(language_code, dir_suffix)

# close_system
close_system(language_code)
print("Done")
