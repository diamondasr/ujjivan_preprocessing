from shell_utils import generic_shell

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

def g2p_create_lexicon(input_lexicon_file,output_lexicon_file,language_code):
    '''
    call g2p script to take list of words and convert it into final lexicon

     ~/nv-g2p/rule/lexicon_post_process.sh "hindi" ~/datasets/rich_transcription/hin_regional/lexicon_input.txt ~/datasets/rich_transcription/hin_regi\
onal/lexicon_final.txt
    '''

    print("Running G2p and creating final lexicon file")

    shell_command="~/g2p/rule/lexicon_post_process.sh " + g2p_lang_dictionary[language_code] + " " + input_lexicon_file + " " + output_lexicon_file
    generic_shell(shell_command,"logs/" + language_code + ".g2p.log")
