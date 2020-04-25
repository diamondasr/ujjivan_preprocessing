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


current_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
conversion_file_set=set() # this basically stores all utterance ids of files already converted to wav
words_set = set() # a set to store words for lexicon
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


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

def generic_shell(shell_command,log_file_name):
    """
        this defines a python function which can run any shell script command
        from python and route logs to log file 
    """

    try:
        #print(shell_command.split())
        process = subprocess.Popen(shell_command,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,shell=True)
        stdout, stderr = process.communicate()

        if stderr:

            shell_logger=setup_logger(log_file_name, log_file_name, level=logging.INFO)
            shell_logger.error(stderr)


    except:
        print("Exception during running generic shell with following command - ")
        shell_logger=setup_logger(log_file_name, log_file_name, level=logging.INFO)
        shell_logger.error(stderr)



def count_lines(file_path):
    with open(file_path) as foo:
        lines = len(foo.readlines())
    return lines


def rm_unnecessary_files(language_code):
    """ this functions deletes some temporary files , for example before train/test split """

    files_to_remove=['lexicon_left','lexicon.txt','wav.list','test_ids','dataset_ids','train_ids']
    for file in files_to_remove:
        remove_file(file)


def write_list_to_file(my_list,filepath):
    """
    a simple utility function to write a python list to file 
    """
    with open(filepath, mode='wt', encoding='utf-8') as myfile:
        myfile.write('\n'.join(my_list))

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

def create_dir(dir_path,language_code):
    if not os.path.isdir(dir_path):
        generic_shell("mkdir " + dir_path ,"logs/" + language_code + "." + "mkdir.log")


def create_kaldi_directories(language_code,destination_wav_dir,create_subset_split_dirs=False):
    """ this function generates folder structure which kaldi expects, also creates some general directories not for kaldi
    """
    wav_scp_count=0
    mkdir_dirs=["logs","data","data/" + language_code , "kaldi_outputs" , "kaldi_outputs/" + language_code]
    for dir in mkdir_dirs:
        create_dir(dir,language_code)
        

    if create_subset_split_dirs==True:

        if not os.path.isfile("kaldi_outputs/" +   "wav.scp"):
            # this means all files were already processed so there is no new file
            print("not creating new split since no new file present")
            return
        
        # read the length of wav.scp in kaldi_outputs/language_id
        wav_scp_count=str(count_lines("kaldi_outputs/"  + "wav.scp"))

        # check if wav_scp_count is present in file called .subsets.txt in kaldi_outputs/language_id
        # if yes skip , dont do anything, if not create a subdirectory in kaldi_outputs/language_id called language_id_wav_scp_count
        
        if os.path.isfile("kaldi_outputs/" +  language_code + "/.subsets.txt"):
            print ("subset file exists for language")
            print("wav scp count : ")
            print(wav_scp_count)

            subset_counts=read_file_to_list("kaldi_outputs/" +  language_code + "/.subsets.txt")
            
            if wav_scp_count in subset_counts:
                print("split directory already existing")
            else:
                print("split directory doesnt exist, creating ..")
                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count,"logs/" + language_code + "." + "mkdir.log")
                shell_command="cp kaldi_outputs/wav.scp kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count
                shell_command2="cp kaldi_outputs/text kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count
                shell_command3="cp kaldi_outputs/spk2utt kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count
                shell_command4="cp kaldi_outputs/utt2spk kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count
                
                shell_command5="cp data/" + language_code +  "/lexicon.txt kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count

                cp_shell_commands=[shell_command,shell_command2,shell_command3,shell_command4,shell_command5]
                for command in cp_shell_commands:
                    generic_shell(command, "logs/" + language_code + "." + "cp.log" )


                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data","logs/" + language_code + "." + "mkdir.log")
        

        else:
            print ("subsets.txt doesnt exist creating it for the first time")
            generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count,"logs/" + language_code + "." + "mkdir.log")
            shell_command2="cp data/" + language_code +  "/lexicon.txt kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count
            generic_shell(shell_command2,"logs/" + language_code + "." + "cp.log")
            append_row_file("kaldi_outputs/" +  language_code + "/.subsets.txt",wav_scp_count)

            shell_command="cp kaldi_outputs/wav.scp kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count
            shell_command2="cp kaldi_outputs/text kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count
            shell_command3="cp kaldi_outputs/spk2utt kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count
            shell_command4="cp kaldi_outputs/utt2spk kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count
            generic_shell(shell_command,"logs/" + language_code + "." + "cp.log")
            generic_shell(shell_command2,"logs/" + language_code + "." + "cp.log")
            generic_shell(shell_command3,"logs/" + language_code + "." + "cp.log")
            generic_shell(shell_command4,"logs/" + language_code + "." + "cp.log")

            generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data","logs/" + language_code + "." + "mkdir.log")

    if not os.path.isdir("logs"):
        generic_shell("mkdir logs","logs/" + language_code + "." + "mkdir.log")

    if not os.path.isdir(destination_wav_dir):
        generic_shell("mkdir " + destination_wav_dir ,"logs/" + language_code + "." + "mkdir.log")
    #generic_shell("mkdir audios","logs/" + language_code + "." + "mkdir.log")
    if not os.path.isdir(destination_wav_dir  + language_code):
        generic_shell("mkdir " + destination_wav_dir + language_code ,"logs/" + language_code + "." + "mkdir.log")
    
    return language_code + "_" + str(wav_scp_count) # this will be used by other functions later, to store files in this subset



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

def append_row_file(file,row):
    """

    general function which appends data row to a text file

    """

    with open(file, "a") as myfile:
        myfile.write(row + "\n")
        
def create_wav_list_file(wav_file_path,wav_list_path,wav_scp_path):
    """

    appends audio file path to wav_list file each new data row
    also appends to wav.scp file

    """

    utterance_id=wav_file_path.split("/")[-1].replace(".wav","")
    append_row_file(wav_list_path,wav_file_path)
    append_row_file(wav_scp_path,utterance_id + " " + wav_file_path)


def create_text_file(wav_file_path,text_file_path,transcription_filepath):
    """
    appends to kaldi text ( data/text ) file 
    """

    sentence_id=wav_file_path.split("_")[2].split('.')[0]
    transcription=read_transcription(sentence_id,transcription_filepath)
    text_line=wav_file_path.split("/")[-1].replace(".wav","") + " " +  transcription
    append_row_file(text_file_path,text_line)


def check_if_file_exists(filepath):   
    return os.path.isfile(filepath)

def write_json_to_file(json_object,filepath):
    import json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_object, f, ensure_ascii=False, indent=4)

def write_lexicon(words_set,output_lexicon_path):
    """ given a set having unique words , write one word to each line
    this file will be input to the g2p """

    with open(output_lexicon_path, "w") as lexicon_output:
            for word in list(words_set):
                lexicon_output.write(word + "\n")

def g2p_create_lexicon(input_lexicon_file,output_lexicon_file,lexicon_language_code,language_code):
    '''
    call g2p script to take list of words and convert it into final lexicon

     ~/nv-g2p/rule/lexicon_post_process.sh "hindi" ~/datasets/rich_transcription/hin_regional/lexicon_input.txt ~/datasets/rich_transcription/hin_regi\
onal/lexicon_final.txt
    '''

    print("Running G2p and creating final lexicon file")

    shell_command="~/nv-g2p/rule/lexicon_post_process.sh " + lexicon_language_code + " " + input_lexicon_file + " " + output_lexicon_file
    generic_shell(shell_command,"logs/" + language_code + ".g2p.log")

def download_transcriptions(final_text_url,destination_transcription_file,temp_lexicon_path,final_lexicon_path,lexicon_language_code,language_code):
    """ downloads transcriptions , but if already present doesnt download again 
    """

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
                append_row_file(destination_transcription_file,transcription_row)

        # create lexicon file here
        write_lexicon(words_set,temp_lexicon_path)

        # call g2p script here
        g2p_create_lexicon(temp_lexicon_path,final_lexicon_path,lexicon_language_code,language_code)



    except Exception as ex:
        #print(ex)
        print("exception in download transcriptions function")
        logging.error(logging.traceback.format_exc())


def remove_file(filepath):
    """
        utility function to remove a file but checks if it exists before removing it
    """

    if os.path.isfile(filepath):
        os.remove(filepath)
        
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
    #print(stdout, stderr)

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

def download_audio_json(final_audio_url,destination_audio_file):
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
        return read_json_from_file(destination_audio_file)


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
        if utterance_id in  conversion_file_set:
            return

        output_destination_path=destination_wav_directory + output_wav_filename
        convert_mp3_to_wav(destination_path,destination_wav_directory ,language_code )

        conversion_file_set.add(utterance_id)

        create_wav_list_file(output_destination_path,wav_list_file,wav_scp_path)
        downloaded_audio_count=downloaded_audio_count + 1

        create_text_file(output_destination_path, text_filepath,transcription_filepath)

        append_row_file(spk2utt_filepath, utterance_id + "_" + speaker_id + " " + utterance_id )
        append_row_file(utt2spk_filepath, utterance_id + " " + utterance_id + "_" + speaker_id )

        return destination_path

    except Exception as ex:
        print("exception during convert single file function")
        logging.error(logging.traceback.format_exc())

