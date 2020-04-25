# Author Saurabh Vyas , Navanatech

"""

This script has common utility functions, and is used by main download.py script

"""




import subprocess
import logging

import json
import urllib.request, json 
import urllib
#from urlparse import urlparse
from os.path import splitext

import logging 
import os.path
import os
from datetime import datetime
import _pickle as pickle


current_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#wav_list_path= os.getcwd() + "/wav.list"
#wav_scp_path= os.getcwd() + "/kaldi_outputs/wav.scp"
#text_filepath= os.getcwd() + "/kaldi_outputs/text"
#language_code="ta"
#transcription_filepath= os.getcwd() + "/data/" + language_code + "/transcriptions.txt"
#spk2utt_filepath= os.getcwd() + "/kaldi_outputs/spk2utt"
#utt2spk_filepath= os.getcwd() + "/kaldi_outputs/utt2spk"

#destination_wav_directory= os.getcwd() + "/wavs/" + language_code + "/"

#lexicon_language_code="tamil"
conversion_file_set=set() # this basically stores all utterance ids of files already converted to wav



#temp_lexicon_path= os.getcwd() + "/lexicon_left"
#final_lexicon_path=os.getcwd() + "/lexicon.txt"

#final_kaldi_dataset_dir="kaldi_outputs_final" # after train/test split

words_set = set() # a set to store words for lexicon



#process = subprocess.Popen(['echo', 'More output'],
 #                    stdout=subprocess.PIPE, 
  #                   stderr=subprocess.PIPE)
#stdout, stderr = process.communicate()
#stdout, stderr


formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def hasNumbers(inputString):
    """ checks if string has numbers or not"""
    return any(char.isdigit() for char in inputString)


def write_pickle_file(python_object,destination_filename):
    """
        writes a python dict to a file
    """

    with open(destination_filename, 'wb') as file:
     file.write(pickle.dumps(python_object))

def load_pickle_file(filename):
    """ loads python dict from pickle file"""

    try:
        f = open(filename)
        # Do something with the file
        with open(filename, 'rb') as handle:
            python_object = pickle.load(handle)

            return python_object


    except IOError:
        print("Pickle File not accessible")

    
def init_system(language_code):
    """
    Basically does some initialization stuff like loading some files
    """
    global conversion_file_set
    my_set=load_pickle_file("."+ language_code + ".set")
    conversion_file_set = my_set
    
    #Create and configure logger 
    logging.basicConfig(filename="logs/"  + language_code + ".main.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w')
    #Creating an object 
    logger=logging.getLogger() 
  
    #Setting the threshold of logger to DEBUG 
    logger.setLevel(logging.DEBUG) 

    
    #print("conversion file set : ")
    #print(conversion_file_set)

    #print("activate conda environment g2p")
    #generic_shell("conda activate g2p","logs/" + language_code + "." + "conda.log")


    if conversion_file_set == None:
        conversion_file_set=set()
    else:
        print(str(len(conversion_file_set)) + " files have already been converted to wav so will skip those for language " + language_code )




def close_system(language_code):
    """
    Basically does some final post processing like storing stateof dictionary etc
    """
    global conversion_file_set
    #print("conversion file set : ")
    #print(conversion_file_set)
    write_pickle_file(conversion_file_set,"."+ language_code + ".set" )






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
        #stdout, stderr
        #print(stdout)

        if stderr:
            print(stderr)
            print("Exception during running generic shell with following command - ")
            print(shell_command)
            shell_logger=setup_logger(log_file_name, log_file_name, level=logging.INFO)
            print(shell_command)

            shell_logger.error(stderr)


        

        #logging.error("stdout")
        #logger = setup_logger('shell_logger', log_file_name)
    #logger.info(stdout)
          

    
    #logger = setup_logger('shell_logger', log_file_name)
    #
    except:
        print("Exception during running generic shell with following command - ")
        shell_logger=setup_logger(log_file_name, log_file_name, level=logging.INFO)
        shell_logger.error(stderr)
        #print(shell_command)

    
        #shell_logger.info(stderr)
        #print("exception has occurred, please refer to log file " + log_file_name)


def count_lines(file_path):
    with open(file_path) as foo:
        lines = len(foo.readlines())
    return lines

def create_kaldi_subset(wav_scp_path,final_kaldi_dataset_dir,language_code,suffix_dir):


    "creates a subset of data for train and test"
    """
    suffix_dir is something like ta_15000 , we need this to create subdirectories
    we assume the split directory like kaldi_outputs/ta/ta_15k has already been created

    """
    print("creating train and test split")

    shell_command1="awk '{ print $1 }' " + wav_scp_path + " > dataset_ids"
    generic_shell(shell_command1,"logs/" + language_code + "." + "subset.log")

    lines_dataset=count_lines("./dataset_ids")
    print("total rows in dataset : " + str(lines_dataset))
    test_lines=int(0.1 * lines_dataset)
    print("total rows in testset : " + str(test_lines))
    
    subset_choice=input("How would you like to create test split ? choose 1 for default sentence based split , if not enter 2 please create file test_ids in same folder (you can use the generated dataset_ids file)")
    
    if subset_choice=="1":
        print("by default usng 10 percent of overall data for test set")
        shell_command2="shuf -n " + str(test_lines) + " dataset_ids > test_ids  "

    elif subset_choice=="2":
        print("using users test_ids file for splitting")


   
    

    
    shell_command3="cat dataset_ids | grep -v -f test_ids > train_ids"

    shell_command4="cat kaldi_outputs/wav.scp | grep  -f train_ids > kaldi_outputs/" + language_code + "/" + suffix_dir + "/data/train/wav.scp"
    shell_command5="cat kaldi_outputs/text | grep  -f train_ids > kaldi_outputs/" + language_code + "/" + suffix_dir + "/data/train/text"
    shell_command6="cat kaldi_outputs/spk2utt | grep  -f train_ids > kaldi_outputs/" + language_code + "/" + suffix_dir + "/data/train/spk2utt"


    shell_command7="cat kaldi_outputs/wav.scp | grep  -f test_ids > kaldi_outputs/" + language_code + "/" + suffix_dir + "/data/test/wav.scp"
    shell_command8="cat kaldi_outputs/text | grep  -f test_ids > kaldi_outputs/" + language_code + "/" + suffix_dir + "/data/test/text"
    shell_command9="cat kaldi_outputs/spk2utt | grep  -f test_ids > kaldi_outputs/" + language_code + "/" + suffix_dir + "/data/test/spk2utt"

    shell_command10="cat kaldi_outputs/utt2spk | grep  -f train_ids > kaldi_outputs/" + language_code + "/" + suffix_dir + "/data/train/utt2spk"
    shell_command11="cat kaldi_outputs/utt2spk | grep  -f test_ids > kaldi_outputs/" + language_code + "/" + suffix_dir + "/data/test/utt2spk"



    generic_shell(shell_command2,"logs/" + language_code + "." + "subset.log")
    generic_shell(shell_command3,"logs/" + language_code + "." + "subset.log")
    generic_shell(shell_command4,"logs/" + language_code + "." + "subset.log")
    generic_shell(shell_command5,"logs/" + language_code + "." + "subset.log")
    generic_shell(shell_command6,"logs/" + language_code + "." + "subset.log")
    generic_shell(shell_command7,"logs/" + language_code + "." + "ssubset.log")
    generic_shell(shell_command8,"logs/" + language_code + "." + "subset.log")
    generic_shell(shell_command9,"logs/" + language_code + "." + "subset.log")
    generic_shell(shell_command10,"logs/" + language_code + "." + "subset.log")
    generic_shell(shell_command11,"logs/" + language_code + "." + "subset.log")
    ####shuf -n 100 $audio_dir/wav.list > $audio_dir/test_wav.list                                                                                        
    ####cat $audio_dir/wav.list | grep -v -f $audio_dir/test_wav.list > $audio_dir/train_wav.list 

    #utils/subset_data_dir.sh --utt-list

    #generic_shell("","logs/subset.log")


def rm_unnecessary_files(language_code):
    """ this functions deletes some temporary files , for example before train/test split """
    #generic_shell("rm  kaldi_outputs/wav.scp","logs/" + language_code + "." + "rm.log")
    #generic_shell("rm  kaldi_outputs/text","logs/" + language_code + "." + "rm.log")
    #generic_shell("rm  kaldi_outputs/spk2utt","logs/" + language_code + "." + "rm.log")
    #generic_shell("rm  lexicon_left","logs/" + language_code + "." + "rm.log")
    #generic_shell("rm  lexicon.txt","logs/" + language_code + "." + "rm.log")
    #generic_shell("rm  wav.list","logs/" + language_code + "." + "rm.log")

    remove_file("kaldi_outputs/wav.scp")
    remove_file("kaldi_outputs/text")
    remove_file("kaldi_outputs/spk2utt")
    remove_file("kaldi_outputs/utt2spk")
    remove_file("lexicon_left")
    remove_file("lexicon.txt")
    remove_file("wav.list")
    remove_file("test_ids")
    remove_file("dataset_ids")
    remove_file("train_ids")




def read_file_to_list(filepath):
    """
        simple utility function which basically reads input file having one entry in each line
        to a python list 

    """

    with open(filepath) as f:
        return f.read().splitlines() 


def create_new_data_variant(language_code):
    """
        This function basically reads a file called kaldi_outputs/lang_id/.subsets.txt which has number of rows in existing subsets
        if new dataset rows is not in this list then it creates a new subset

    """
def create_kaldi_directories(language_code,destination_wav_dir,create_subset_split_dirs=False):
    """ this function generates folder structure which kaldi expects, also creates some general directories not for kaldi
         
    """

    wav_scp_count=0

    # kaldi specific
    #generic_shell("rm -rf kaldi_outputs","logs/rm.log")

    if not os.path.isdir("logs"):
        generic_shell("mkdir logs" ,"logs/" + language_code + "." + "mkdir.log")

    # check if kaldi_outputs exist
    if not os.path.isdir("data"):
        generic_shell("mkdir data" ,"logs/" + language_code + "." + "mkdir.log")

    if not os.path.isdir("data/" + language_code):
        generic_shell("mkdir data/" + language_code ,"logs/" + language_code + "." + "mkdir.log")


    if not os.path.isdir("kaldi_outputs"):
        generic_shell("mkdir kaldi_outputs" ,"logs/" + language_code + "." + "mkdir.log")
    
    if not os.path.isdir("kaldi_outputs/" + language_code ):
            generic_shell("mkdir kaldi_outputs/"  +  language_code ,"logs/" + language_code + "." + "mkdir.log")



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
                generic_shell(shell_command,"logs/" + language_code + "." + "cp.log")
                generic_shell(shell_command2,"logs/" + language_code + "." + "cp.log")
                generic_shell(shell_command3,"logs/" + language_code + "." + "cp.log")
                generic_shell(shell_command4,"logs/" + language_code + "." + "cp.log")
                generic_shell(shell_command5,"logs/" + language_code + "." + "cp.log")

                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data","logs/" + language_code + "." + "mkdir.log")
                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data/local","logs/" + language_code + "." + "mkdir.log")
                generic_shell("mkdir kaldi_outputs/" +   language_code + "/" + language_code + "_" + wav_scp_count + "/data/local/dict","logs/" + language_code + "." + "mkdir.log")
                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data/train","logs/" + language_code + "." + "mkdir.log")
                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count +  "/data/test","logs/" + language_code + "." + "mkdir.log")
                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/exp","logs/" + language_code + "." + "mkdir.lsog")
                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/mfcc","logs/" + language_code + "." + "mkdir.log")
                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data/local/data","logs/" + language_code + "." + "mkdir.log")
                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count +  "/data/local/lm_temp","logs/" + language_code + "." + "mkdir.log")
                generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data/local/kaldi_lm","logs/" + language_code + "." + "mkdir.log")


                



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
            generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data/local","logs/" + language_code + "." + "mkdir.log")
            generic_shell("mkdir kaldi_outputs/" +   language_code + "/" + language_code + "_" + wav_scp_count + "/data/local/dict","logs/" + language_code + "." + "mkdir.log")
            generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data/train","logs/" + language_code + "." + "mkdir.log")
            generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count +  "/data/test","logs/" + language_code + "." + "mkdir.log")
            generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/exp","logs/" + language_code + "." + "mkdir.lsog")
            generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/mfcc","logs/" + language_code + "." + "mkdir.log")
            generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data/local/data","logs/" + language_code + "." + "mkdir.log")
            generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count +  "/data/local/lm_temp","logs/" + language_code + "." + "mkdir.log")
            generic_shell("mkdir kaldi_outputs/" +  language_code + "/" + language_code + "_" + wav_scp_count + "/data/local/kaldi_lm","logs/" + language_code + "." + "mkdir.log")

    # non kaldi
    #generic_shell("rm -rf logs","logs/rm.log")
    if not os.path.isdir("logs"):
        generic_shell("mkdir logs","logs/" + language_code + "." + "mkdir.log")
    #generic_shell("rm -rf wavs","logs/rm.log")
    #generic_shell("rm -rf audios","logs/" + language_code + "." + "rm.log")
    if not os.path.isdir(destination_wav_dir):
        generic_shell("mkdir " + destination_wav_dir ,"logs/" + language_code + "." + "mkdir.log")
    #generic_shell("mkdir audios","logs/" + language_code + "." + "mkdir.log")
    if not os.path.isdir(destination_wav_dir  + language_code):
        generic_shell("mkdir " + destination_wav_dir + language_code ,"logs/" + language_code + "." + "mkdir.log")
    
    return language_code + "_" + str(wav_scp_count) # this will be used by other functions later, to store files in this subset


    
#from datetime import datetime

#timestamp = 1545730073
#dt_object = datetime.fromtimestamp(timestamp)

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
    #print("sentence id")
    #print(sentence_id)
    transcription=read_transcription(sentence_id,transcription_filepath)
    #print("transcription")
    #print(transcription)
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

def remove_file(filepath):
    """
        utility function to remove a file but checks if it exists before removing it
    """

    if os.path.isfile(filepath):
        os.remove(filepath)



def create_kaldi_lang(language_code,suffix_dir,lexicon_path):
    """
        creates file in kaldis data/local/lang directory
        
         suffix_dir is something like ta_15000 , we need this to create subdirectories
    we assume the split directory like kaldi_outputs/ta/ta_15k has already been created

    """

    #cat $dir/lexicon.txt | sed 's:[[:space:]]: :g' | cut -d" " -f2- - | tr ' ' '\n' | sort -u > $dir/phones_t.txt
#sed -i -e '/^\s*$/d' $dir/phones_t.txt
#grep -v -E '!SIL' $dir/phones_t.txt > $dir/phones.txt

#grep -v -F -f $dir/silence_phones.txt $dir/phones.txt > $dir/nonsilence_phones.txt


    #lexicon.txt
    shell_command0="cp " + lexicon_path + " " + kaldi_outputs/" + language_code + "/" +  suffix_dir + "/data/local/dict"
    generic_shell(shell_command0,"logs/" + language_code + "." + "kaldi_data_lang.log")

    
    #shell_command1="cut -d ' ' -f 2- ./lexicon.txt |  sed 's/ /\n/g' |   sort -u > kaldi_outputs/data/local/dict/nonsilence_phones.txt"


    #generic_shell(shell_command1,"logs/kaldi_data_lang.log")

    # silence_phones.txt
    shell_command2="echo  SIL > kaldi_outputs/" + language_code + "/" +  suffix_dir  + "/data/local/dict/silence_phones.txt"
    generic_shell(shell_command2,"logs/" + language_code + "." + "kaldi_data_lang.log")

    shell_command3="echo 'SIL' > kaldi_outputs/" + language_code + "/" +  suffix_dir + "/data/local/dict/optional_silence.txt"
    generic_shell(shell_command3,"logs/" + language_code +  "." + "kaldi_data_lang.log")

    # nonsilence_phones.txt
    shell_command4="cat " + lexicon_path + "  | sed 's:[[:space:]]: :g' | cut -d' ' -f2- - | tr ' ' '\n' | sort -u > kaldi_outputs/" + language_code + "/" +  suffix_dir + "/data/local/dict/phones_t.txt"
    shell_command5=r"sed -i -e '/^\s*$/d' kaldi_outputs/" + language_code + "/" +  suffix_dir + "/data/local/dict/phones_t.txt"
    shell_command6="grep -v -E '!SIL' kaldi_outputs/" + language_code + "/" +  suffix_dir + "/data/local/dict/phones_t.txt > kaldi_outputs/" + language_code + "/" +  suffix_dir + "/data/local/dict/phones.txt"
    shell_command7="grep -v -F -f kaldi_outputs/" + language_code + "/data/local/dict/silence_phones.txt kaldi_outputs/" + language_code + "/data/local/dict/phones.txt > kaldi_outputs/" + language_code + "/data/local/dict/nonsilence_phones.txt"

    generic_shell(shell_command4,"logs/" + language_code + "." + "kaldi_data_lang.log")
    generic_shell(shell_command5,"logs/" + language_code + "." + "kaldi_data_lang.log")
    generic_shell(shell_command6,"logs/" + language_code + "." + "kaldi_data_lang.log")
    generic_shell(shell_command7,"logs/" + language_code + "." + "kaldi_data_lang.log")

    shell_command8="cp kaldi_outputs/" + language_code + "/" +  suffix_dir + "/data/train/text kaldi_outputs/" + language_code + "/data/local/data/train.text"
    generic_shell(shell_command8,"logs/" + language_code + "." + "kaldi_data_lang.log")

    #${x}.text >${x}.stm
    # create stm files for sclite scoring
    shell_command9="cp kaldi_outputs/" + language_code + "/" +  suffix_dir + "/data/train/text kaldi_outputs/" + language_code + "/data/local/data/train.stm"
    shell_command10="cp kaldi_outputs/" + language_code + "/" +  suffix_dir + "/data/test/text kaldi_outputs/" + language_code + "/data/local/data/test.stm"

    generic_shell(shell_command9,"logs/" + language_code + "." + "kaldi_data_lang.log")
    generic_shell(shell_command10,"logs/" + language_code + "." + "kaldi_data_lang.log")

    # Create dummy GLM file for sclite:  




        
def convert_mp3_to_wav(mp3_path,output_wav_dir,language_code):

    """

    returns True if conversion was successfull , else returns False
    if destination file already exists, by default it replaces it -y flag

    """
    #/usr/bin/ffmpeg -i mp3_dir/$file wav_dir/${out_file}_tmp.wav; 
    #sox wav_dir/${out_file}_tmp.wav -c1 -r16000 -b16 wav_dir/${out_file}.wav ;


    #print("converting file " + mp3_path )
    out_file_temp=  mp3_path.split("/")[-1].replace(".mp3",".temp.wav")
    out_file=  mp3_path.split("/")[-1].replace(".mp3",".wav")

    process = subprocess.Popen(['/usr/bin/ffmpeg' ,'-hide_banner' ,'-nostats', '-y', '-i', mp3_path , output_wav_dir + out_file_temp]
                     ,stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    #print(stdout, stderr)

    if stderr:
        #ssprint("error during ffmpeg ")
        #logging.error(stdout)
        logging.error(stderr)

    process2 = subprocess.Popen(['sox', output_wav_dir + out_file_temp , '-c1' , '-r16000' , '-b16',output_wav_dir + out_file]
                     ,stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    stdout2, stderr2 = process2.communicate()
    #print(stdout2, stderr2)

    # remove temp wav file
    shell_command="rm " + output_wav_dir + out_file_temp 
    generic_shell(shell_command,"logs/" + language_code + "." + "rm.log")

    if stderr2:
        #print("error during sox ")
        #logging.error(stdout)
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
    downloads mp3 file
    converts mp3 to wav file
    updates wav.list file
    updates wav.scp file
    updates kaldi_outputs/text file
    updates spk2utt file
    """
    try:
        #print("downloading single audio file")
        #global downloaded_audio_count
        
        destination_filename= url.split("/")[-1]
        #destination_path=destination_directory + destination_filename
        #urllib.request.urlretrieve(url, destination_path)
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
        #print("speaker id ;")
        #print(speaker_id)
        #create_text_file(speaker_id + " " + output_wav_filename, spk2utt_filepath)
        append_row_file(spk2utt_filepath, utterance_id + "_" + speaker_id + " " + utterance_id )
        append_row_file(utt2spk_filepath, utterance_id + " " + utterance_id + "_" + speaker_id )

        return destination_path

    except Exception as ex:
        print("exception during convert single file function")
        logging.error(logging.traceback.format_exc())

def download_audio_list(audio_list, destination_directory ):
    """
        input : a list of urls storing audio files
        output : if no error return true, else return -1
    """

    for url in audio_list:
        file_name=url.split("/")[-1]

        urllib.request.urlretrieve(url, destination_directory + file_name)
