"""
# Author Saurabh Vyas , Navanatech

This python3 script takes audio source url as input and downloads audio data and filters it 
according to parameters

It also logs important information such as number of audio files downloaded

Please create a directiory called audios and wavs in same folder

"""
import json
import urllib.request, json 
import urllib.parse
#from urlparse import urlparse
from os.path import splitext
from tqdm import tqdm
import logging 
from data_utils import download_transcriptions,create_kaldi_directories,write_json_to_file,check_if_file_exists,download_audio_json , read_json_from_file , download_single_file,convert_mp3_to_wav
                       
  
#Create and configure logger 
logging.basicConfig(filename="./script.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w')
#Creating an object 
logger=logging.getLogger() 
  
#Setting the threshold of logger to DEBUG 
logger.setLevel(logging.DEBUG) 

audio_source="https://vca-admin.azurewebsites.net/v1/audio?passcode=N@v4n473ch&language_code="
text_source="https://vca-admin.azurewebsites.net/v1/sentence?passcode=N@v4n473ch&language_code="
language_code="ta"
speaker_id="127"  # default value is -1 
extension=".mp3" # default value is -1 
final_audio_url=audio_source + language_code
final_text_url=text_source + language_code

destination_directory="./audios/"
destination_wav_directory="./wavs/"
wav_list_path="./wav.list"
destination_transcription_file="./transcriptions.txt"
destination_audio_file="./audio.json"

epoch_start=-1
epoch_end=-1


downloaded_audio_count=0
number_of_rows=50 # how many data items do you need in dataset
empty_transcript_counter=0


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


# create kaldi directory structure
create_kaldi_directories()

# download transcriptions
download_transcriptions(final_text_url,destination_transcription_file)

# download audio json
data=download_audio_json(final_audio_url,destination_audio_file,"./audio.json")


data=data["data"]
# see if specific speaker id is provided
    

if speaker_id != -1:
    print("filtering according to specific speaker")
    data=data[speaker_id]
    #print(data[speaker_id])
    #print(data)
    for row in tqdm(data):
        #print(row)
        extension_valid=check_file_extension(row,extension)
        #print(extension_valid)

        if extension_valid:
                    # download audio
                    #print("downloading audio for row")
                    #download_single_file(row)
                    destination_mp3_path=download_single_file(row,downloaded_audio_count,destination_directory,speaker_id)
                    #basename=destination_mp3_path.split("/")[-1]
                    
                    
                    #convert_mp3_to_wav(destination_mp3_path,destination_wav_directory  )

else:
    print("speaker filtering disabled ")
    for speaker_id in data:
        for row in speaker_id:
            extension_valid=check_file_extension(row,extension)
            if extension_valid:
                
                    # download audio
                    destination_mp3_path=download_single_file(row,downloaded_audio_count,destination_directory,speaker_id)


                    #convert_mp3_to_wav(mp3_path,output_wav_dir)
                    









