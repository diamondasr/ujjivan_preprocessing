from shell_utils import generic_shell


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

    shell_command="~/g2p/rule/lexicon_post_process.sh " + lexicon_language_code + " " + input_lexicon_file + " " + output_lexicon_file
    generic_shell(shell_command,"logs/" + language_code + ".g2p.log")