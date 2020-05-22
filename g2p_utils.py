from shell_utils import generic_shell
from contextlib import contextmanager
from file_utils import remove_file
import os

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

# maps from data lang id to its corresponding g2p language id
g2p_lang_dictionary = { 'ta':'tamil','te':'telegu', \
'gu':'gujrati' , 'ka':'Kannada', 'ma':'malayalam' , 'od':'odia','be':'bengali','as':'assamese' \
, 'hi':'hindi' , 'pu':'punjabi','mar':'marathi' }

def write_lexicon(words_set,output_lexicon_path):
    """ given a set having unique words , write one word to each line
    this file will be input to the g2p """

    with open(output_lexicon_path, "w") as lexicon_output:
            for word in list(words_set):
                lexicon_output.write(word + "\n")

#def g2p_create_lexicon(input_lexicon_file,output_lexicon_file,language_code):
    '''
    call g2p script to take list of words and convert it into final lexicon

     ~/nv-g2p/rule/lexicon_post_process.sh "hindi" ~/datasets/rich_transcription/hin_regional/lexicon_input.txt ~/datasets/rich_transcription/hin_regi\
onal/lexicon_final.txt
    '''

    #print("Running G2p and creating final lexicon file")

    #shell_command="~/g2p/rule/lexicon_post_process.sh " + g2p_lang_dictionary[language_code] + " " + input_lexicon_file + " " + output_lexicon_file
    #generic_shell(shell_command,"logs/" + language_code + ".g2p.log")

def g2p_create_lexicon(input_lexicon_file,output_lexicon_file,language_code):
    """
     calls g2p python script and does some post processing to give final kaldi compatible lexicon file
    """
    g2p_lang_code=g2p_lang_dictionary[language_code]
    log_prefix=str(os.getcwd()) + '/'

    with cd('~/g2p/rule'):
        files_to_remove=['lexicon_temp','lexicon_temp2','lexicon_temp3','lexicon_temp4']
        for f in files_to_remove:
            remove_file(f)
        generic_shell(' python ~/nv-g2p/rule/repl_saurabh.py -f ' + g2p_lang_code + ' ' + input_lexicon_file + ' ' + 'lexicon_temp' , log_prefix + "logs/" + language_code + ".lexicon_post_process.log")
        # create actual lexicon file
        generic_shell('paste ' + input_lexicon_file + ' ' + 'lexicon_temp > lexicon_temp2', log_prefix + "logs/" + language_code + ".lexicon_post_process.log")
        # remove rows with empty pronunciations
        generic_shell("awk '$2!=""' lexicon_temp2 > lexicon_temp3" , log_prefix + "logs/" + language_code + ".lexicon_post_process.log")
        generic_shell('echo "!SIL SIL" >> lexicon_temp3' , log_prefix + "logs/" + language_code + ".lexicon_post_process.log")
        generic_shell('echo "<UNK> SPN" >> lexicon_temp3' , log_prefix + "logs/" + language_code + ".lexicon_post_process.log")
        # remove duplicate rows
        generic_shell("awk '!seen[$0]++' lexicon_temp3 > " + output_lexicon_file  , log_prefix + "logs/" + language_code + ".lexicon_post_process.log")


        