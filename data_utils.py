# Author Saurabh Vyas , Navanatech

"""

This script has common utility functions, and is used by main download.py script

"""

import subprocess
import logging
import json
import urllib.request, json 
import urllib
from os.path import splitext
import logging 
import os.path
import os
from datetime import datetime
import _pickle as pickle
import path
import shutil

current_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
conversion_file_set=set() # this basically stores all utterance ids of files already converted to wav
words_set = set() # a set to store words for lexicon

from file_utils import check_if_file_exists, read_json_from_file,read_file_to_list,write_json_to_file,write_list_to_file,append_row_file,remove_file,convert_mp3_to_wav
from g2p_utils import write_lexicon,g2p_create_lexicon
from kaldi_utils import create_wav_list_file,create_text_file,create_kaldi_directories

def init_system(language_code):
    """
    Basically does some initialization stuff like loading some files
    """
    global conversion_file_set
    #my_set=load_pickle_file("."+ language_code + ".set")
    filepath="data/" + language_code + "/" + language_code + ".set"
    my_set=set(read_file_to_list(filepath))
    conversion_file_set = my_set
    
    #Create and configure logger 
    logging.basicConfig(filename="logs/"  + language_code + ".main.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w')
    #Creating an object 
    logger=logging.getLogger() 
  
    #Setting the threshold of logger to DEBUG 
    logger.setLevel(logging.DEBUG) 
    print(str(len(conversion_file_set)) + " files have already been converted to wav so will skip those for language " + language_code )

def close_system(language_code):
    """
    Basically does some final post processing like storing stateof dictionary etc
    """
    global conversion_file_set
    filepath="data/" + language_code + "/" + language_code + ".set"
    write_list_to_file(list(conversion_file_set),filepath)

def filter_line(line):
    """ filters comma,exclamation,question mark, punctuation marks, paranthesis """
    punctuations = r'''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    no_punct = ""
    for char in line:
        if char not in punctuations:
            no_punct = no_punct + char
    return no_punct
    
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

def download_transcriptions(final_text_url,destination_transcription_file,temp_lexicon_path,final_lexicon_path,lexicon_language_code,language_code,generate_lexicon=True):
    """ 
    downloads transcriptions , but if already present doesnt download again 
    """
    try:
        print("downloading transcriptions json")
        with urllib.request.urlopen(final_text_url) as url:
            transcription_json = json.loads(url.read().decode())
        transcription_json=transcription_json["data"]
        for sentence in transcription_json:
            sentence_id=sentence["id"]
            sentence_transcript=sentence["sentence"]
            sentence_transcript=filter_line(sentence_transcript) # remove punctuations     
            # extract words from sentence and add to a set, for creation of lexicon
            for word in sentence_transcript.split():
                # print(word)                                                                                                                         
                words_set.add(word)
            # check if sentence is empty
            if sentence_transcript=="":
                empty_transcript_counter=empty_transcript_counter + 1
            
            else:
                # write the sentence to transcription file
                transcription_row=str(sentence_id) + " " + str(sentence_transcript)
                # make sure if transcriptions file is already present we remove it 
                remove_file(destination_transcription_file)
                append_row_file(destination_transcription_file,transcription_row)

        if (generate_lexicon):
            logging.info("automatically generating lexicon")
            # create lexicon file here
            write_lexicon(words_set,temp_lexicon_path)
            logging.info("generating left side of lexicon")
            # call g2p script here
            g2p_create_lexicon(temp_lexicon_path,final_lexicon_path,lexicon_language_code,language_code)

        else:
            print("not generating lexicon, assuming manually generated lexicon file is placed in data/" + language_code )

    except Exception as ex:
        #print(ex)
        print("exception in download transcriptions function")
        logging.error(logging.traceback.format_exc())

def download_audio_json(final_audio_url,destination_audio_file):
    # check if file already exists
    with urllib.request.urlopen(final_audio_url) as url:
        data = json.loads(url.read().decode())
        print("downloading audio json")
        write_json_to_file(data,destination_audio_file)
        print("writing audio json")
        return data
    


