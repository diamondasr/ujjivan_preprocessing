from shell_utils import generic_shell
from contextlib import contextmanager
from file_utils import remove_file,remove_duplicate_lines,append_row_file,write_list_to_file
import os
import shutil

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

def g2p_create_lexicon(input_lexicon_file,output_lexicon_file,language_code,words_set,transliteration_map_file_path):
    """
     calls g2p python script and does some post processing to give final kaldi compatible lexicon file
    """
    g2p_lang_code=g2p_lang_dictionary[language_code]
    log_prefix=str(os.getcwd()) + '/'
    write_list_to_file(list(words_set),input_lexicon_file)
    with cd('~/g2p/rule'):
        files_to_remove=['lexicon_temp','lexicon_temp2','lexicon_temp3','lexicon_temp4','lexicon_temp5',\
            'lexicon_temp6','lexicon_temp7','lexicon_temp9']
        for f in files_to_remove:
            remove_file(f)
        generic_shell('python3 ~/g2p/rule/repl_wrapper.py -f ' + g2p_lang_code + ' ' + input_lexicon_file + \
        ' ' + 'lexicon_temp' , log_prefix + "logs/" + language_code + ".lexicon_post_process.log")
        # create actual lexicon file
        generic_shell('paste ' + input_lexicon_file + ' ' + 'lexicon_temp > lexicon_temp2 ',\
         log_prefix + "logs/" + language_code + ".lexicon_post_process.log")
        # remove rows with empty pronunciations
        generic_shell("""awk '$2!=""' lexicon_temp2 > lexicon_temp3 """ , \
        log_prefix + "logs/" + language_code + ".lexicon_post_process.log")
        append_row_file('lexicon_temp3','!SIL SIL')
        append_row_file('lexicon_temp3','<UNK> SPN')
        remove_duplicate_lines('lexicon_temp3','lexicon_temp4')

        # 4. manage failed g2p cases
        generic_shell("""cat lexicon_temp2 | sort | uniq > temp2""",\
         log_prefix + "logs/" + language_code + ".lexicon_post_process.log")

        generic_shell("""cat lexicon_temp4 | sort | uniq > temp3""",\
         log_prefix + "logs/" + language_code + ".lexicon_post_process.log")

        generic_shell("""comm -23 temp2 temp3 > failed_g2p_cases """,\
         log_prefix + "logs/" + language_code + ".lexicon_post_process.log")

        # run python transliteration mapping script which goes through each failed word and uses mapping dictionary file provided to get correct pronunciation
        # its output will be a file with following format
        # english word transliterated version
        generic_shell("""python3 transliterate.py -output_file_path transliteration_output -mapping_file_path """ + transliteration_map_file_path,\
                log_prefix + "logs/" + language_code + ".lexicon_post_process.log")

         # extract second column of above
        generic_shell(""" cut -d ' ' -f 2-  transliteration_output """   + """ > lexicon_temp5 """,\
                log_prefix + "logs/" + language_code + ".lexicon_post_process.log")

        # run g2p again for transliterated words
        generic_shell('python3 ~/g2p/rule/repl_wrapper.py -f ' + g2p_lang_code + ' ' + 'lexicon_temp5' + \
        ' ' + 'lexicon_temp6' , log_prefix + "logs/" + language_code + ".lexicon_post_process.log")

        # then paste the first column of above transliteration mapping python script with g2p output
        generic_shell(""" awk '{ print $1 }' """ + 'transliteration_output' + """ > lexicon_temp7 """,\
                log_prefix + "logs/" + language_code + ".lexicon_post_process.log")

        generic_shell(""" paste lexicon_temp7 lexicon_temp6 > lexicon_temp8  """,\
                log_prefix + "logs/" + language_code + ".lexicon_post_process.log")

        remove_duplicate_lines('lexicon_temp8','lexicon_temp9')

        # finally concatenate it with previous lexicon

        generic_shell(""" cat lexicon_temp4 lexicon_temp9 > lexicon_temp10  """,\
                log_prefix + "logs/" + language_code + ".lexicon_post_process.log")

        shutil.copyfile('lexicon_temp10', output_lexicon_file)
