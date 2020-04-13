import csv
transcription_filepath="./transcriptions.txt"
with open(transcription_filepath) as inf:
    reader = csv.reader(inf, delimiter=" ")
    print(reader)
    for row in reader:
        print(row[0])
