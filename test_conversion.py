from file_utils import convert_mp3_to_wav

mp3_path_valid='/testdatahdd/datasets/ujjivan/voicecollectionblobcontainer/1564488807_117_561.mp3' 
mp3_path='/testdatahdd/datasets/ujjivan/voicecollectionblobcontainer/1564488976_117_485.mp3'
output_wav_dir='/testdatahdd/datasets/ujjivan/wavs/'
language_code='ta'

result=convert_mp3_to_wav(mp3_path_valid,output_wav_dir,language_code)
print(result)
