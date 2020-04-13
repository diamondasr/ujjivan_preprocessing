"""
This python3 script takes audio source url as input and downloads audio data and filters it 
according to parameters

It also logs important information such as number of audio files downloaded

Please create a directiory called audios in the same directory as this file

"""
import json
import urllib.request, json 
import urllib.parse
#from urlparse import urlparse
from os.path import splitext

import logging 
from data_utils import download_transcriptions,write_json_to_file,check_if_file_exists,download_audio_json , read_json_from_file , download_single_file
                       
  
#Create and configure logger 
logging.basicConfig(filename="./download.log", 
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
    print(file_extension)
    if extension != -1:
        if file_extension == extension:
            return True
        else:
            return False
    else:
        return False


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
    for row in data:
        #print(row)
        extension_valid=check_file_extension(row,extension)
        #print(extension_valid)

        if extension_valid:
                    # download audio
                    print("downloading audio for row")
                    #download_single_file(row)
                    download_single_file(row,downloaded_audio_count,destination_directory)

else:
    print("speaker filtering disabled ")
    for speaker_id in data:
        for row in speaker_id:
            file_extension=get_ext(row)
            if extension != -1:
                if file_extension == extension:
                    # download audio
                    download_single_file(url)
                    









def download_transcriptions(final_text_url,destination_transcription_file):
    try:
        #downloaded_audio_count=downloaded_audio_count + 1

        #urllib.urlretrieve(final_text_url, destination_directory + "transcriptions.json")
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
                transcription_row=sentence_id + " " + sentence_transcript
                append_row_file(destination_transcription_file,transcription_row)


    except Exception as ex:
        print(ex)
        logging.error(logging.traceback.format_exc())


