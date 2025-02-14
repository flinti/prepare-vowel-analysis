#!/usr/bin/python3

#    This script reads vowel information from .TextGrid files and outputs a .csv and .table file.
#
#    The script reads praat TextGrid files (ending in .TextGrid) from the directory ./TextGridCompleted (inside of
#    the same directory you are executing this script from).
#    It outputs the file 'output.csv' and 'output.table.
#    'output.csv' is semicolon-separated and output.table is tab-separated.
#
#    The input TextGrid files are expected to have the following tiers:
#        - Sentence (copied from the input)
#        - Word (interval tier, copied from the input)
#        - Vowel (interval tier, copied from the input)
#        - Length (interval tier, with interval length as text)
#        - Point (point tier)
#        - F1 (point tier, with formant 1 frequency in Hz as text)
#        - F2 (point tier, with formant 2 frequency in Hz as text)
#        - F3 (point tier, with formant 3 frequency in Hz as text)
#    All remaining tiers after these are ignored.
#    The file is expected to be encoded in UTF-16, which is what praat usually outputs. If you use a different encoding,
#    you can change that easily in this script.
#
#    The script assumes that a single character in the 'Vowel' tier corresponds to exactly one vowel. If two characters
#    are written, the script assumes a diphthong. If three are written, it assumes a triphthong.
#    The script has problems with characters composed of many unicode codepoints because python treats those as multiple characters.
#
#    The output table has the following columns:
#    Sample	Speaker	Gender	Word	Vowel	IPA	F1(Hz)	F2(Hz)	F3(Hz)	Duration
#
#    2024 Kathrin Strauch, Christian Strauch

import tgt
import csv
import re
from os import listdir, makedirs
from sys import stderr

inputTextGridDirectory = "TextGridCompleted/"

SPEAKER = "4"
GENDER = "f"
HEADER = ["Sample", "Speaker", "Gender", "Word", "Vowel", "IPA", "F1(Hz)", "F2(Hz)", "F3(Hz)",  "Duration"]

def number_to_str(num):
    return "{:6f}".format(num)

def process_sample(textGridFileName, sampleName, encoding='utf-16'):
    tg = tgt.read_textgrid(textGridFileName, encoding=encoding)

    sentences = tg.tiers[0]
    words = tg.tiers[1]
    vowels = tg.tiers[2]
    lengths = tg.tiers[3]
    points = tg.tiers[4]
    f1s = tg.tiers[5]
    f2s = tg.tiers[6]
    f3s = tg.tiers[7]

    start_time = sentences.start_time
    end_time = sentences.end_time

    print(*[w.text for w in words])
    for w in words:
        print(w.text, "start", w.start_time)
    vowelCount = len(vowels)
    formantCount = len(f1s)
    print("Vowels: ", vowelCount)
    print("Formant sets: ", formantCount)

    rows = []

    formantIndex = 0
    for i in range(len(vowels)):
        vowel = vowels[i]
        # ignore spaces and zero width spaces
        # we are also ignoring the IPA length sign
        vowelText = vowel.text.strip(' \u200bː')

		# we are searching from the end of the tier for the word with a lower start_time than the vowel
		# this gives us the word to which the vowel belongs because the count of words is
		# equal to or lower than the count of vowels (assuming each word has at least one vowel)
        word = ""
        for w in reversed(words):
            if w.start_time <= vowel.start_time:
                word = w.text
                break
        
        print("Vowel", vowelText, "start", vowel.start_time, "word", word)
        # we are assuming that a single vowel is represented by exactly one character here.
        nthong = len(vowelText) > 1
        for ipa in vowelText:
            f1 = f1s[formantIndex]
            f2 = f2s[formantIndex]
            f3 = f3s[formantIndex]

            rows += [[
                sampleName,
                SPEAKER,
                GENDER,
                word,
                vowel.text if nthong else ipa,
                ipa,
                f1.text,
                f2.text,
                f3.text,
                number_to_str(vowel.end_time - vowel.start_time),
            ]]
            formantIndex += 1

	# these assertions should never fail
    if i + 1 != vowelCount:
        raise RuntimeError("vowel count does not match last index")
    if formantIndex != formantCount:
        raise RuntimeError("formant count does not match last index")
    
    return rows

# https://stackoverflow.com/questions/2669059/how-to-sort-alpha-numeric-set-in-python
def sorted_nicely(l): 
    """ Sort the given iterable in the way that humans expect.""" 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

files = sorted_nicely(listdir(inputTextGridDirectory))
print("Processing {} files".format(len(files)))


errors = []
rows = [HEADER]
for i in range(len(files)):
    textGridFile = files[i]
    if not textGridFile.endswith('.TextGrid'):
        continue
    basename = textGridFile.removesuffix('.TextGrid')
    textGridFileName = inputTextGridDirectory + basename + ".TextGrid"
    print(str(i+1) + ". Processing file " + basename)
    try:
        rows += process_sample(textGridFileName, basename)
    except Exception as e:
        err = str(i+1) + ". Error while processing file '" + basename + "': " + str(e)
        errors += [err]
        print(err, file=stderr)

print(len(errors), "errors:")
for e in errors:
    print(e)

with open('output.table', 'w', newline='') as csvfile:
    csvWriter = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerows(rows)
with open('output.csv', 'w', newline='') as csvfile:
    csvWriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerows(rows)
