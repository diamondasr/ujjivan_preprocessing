import csv
import argparse

failed_g2p_cases_file='failed_g2p_cases'

# Create the parser
argument_parser = argparse.ArgumentParser(description='Parser for preprocessing script for Ujjivan')

# Add the arguments
argument_parser.add_argument('-output_file_path',
                       type=str,
                       help='specify the output file path', required=True)

argument_parser.add_argument('-mapping_file_path',
                       type=str,
                       help='specify the transliteration mapping file path', required=True)


args = argument_parser.parse_args()
output_lexicon_file=args.output_file_path

# transliteration mapping file location
mapping_file=args.mapping_file_path  #transliteration_mapping.txt

with open(mapping_file, mode='r') as infile:
            reader = csv.reader(infile,delimiter=':')
            eng_dict = {rows[0]:rows[1].strip() for rows in reader}

            print(eng_dict)

with open(failed_g2p_cases_file) as f, open(output_lexicon_file) as f2:
        failed_words = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        failed_words = [x.strip() for x in failed_words]
        for word in failed_words:
            if word in eng_dict:
                f2.write(word + ' ' + eng_dict[word] + '\n')