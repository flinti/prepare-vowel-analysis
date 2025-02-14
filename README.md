# TextGrid to .table and .csv converter script

This script reads vowel information from .TextGrid files and outputs a .csv and .table file.

The script reads praat TextGrid files (ending in .TextGrid) from the directory ./TextGridCompleted (inside of
the same directory you are executing this script from).
It outputs the file 'output.csv' and 'output.table.
'output.csv' is semicolon-separated and output.table is tab-separated.

The input TextGrid files are expected to have the following tiers:
   - Sentence (copied from the input)
   - Word (interval tier, copied from the input)
   - Vowel (interval tier, copied from the input)
   - Length (interval tier, with interval length as text)
   - Point (point tier)
   - F1 (point tier, with formant 1 frequency in Hz as text)
   - F2 (point tier, with formant 2 frequency in Hz as text)
   - F3 (point tier, with formant 3 frequency in Hz as text)

All remaining tiers after these are ignored.
The file is expected to be encoded in UTF-16, which is what praat usually outputs. If you use a different encoding,
you can change that easily in this script.

The script assumes that a single character in the 'Vowel' tier corresponds to exactly one vowel. If two characters
are written, the script assumes a diphthong. If three are written, it assumes a triphthong.
The script has problems with characters composed of many unicode codepoints because python treats those as multiple characters.

The output table has the following columns:
Sample	Speaker	Gender	Word	Vowel	IPA	F1(Hz)	F2(Hz)	F3(Hz)	Duration

## Dependencies

For this script to work, the `tgt` python package must be installed.
On a terminal, you can do this via
```
pip install tgt
```
Alternatively, use the preferred way of your python distribution to install packages. 

## Authors
Kathrin Strauch, Christian Strauch