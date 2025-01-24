#!/bin/bash

# Copyright (C) J Leadbetter <j@jleadbetter.com>
# Affero GPL v3

###############################################################################
#                                                                             #
#  Turn text into MP3 files with voices provided by Google TTS.               #
#                                                                             #
#  The text file should have one word per line. The script then creates       #
#  an audio file for each word, so they can be practiced independently.       #
#                                                                             #
#  Requires the Google TTS python package:                                    #
#                                                                             #
#      > pip install gTTS==2.5.4                                              #
#                                                                             #
###############################################################################

USAGE="
Usage:
\tfetch_audio.sh [OPTION]... [TEXT-FILE]
\n
Description:
\tConvert text into MP3 files with voices provided by Google Translate.
\tOnly supports Dutch.
\n
\t-d, --dir
\t\tOutput directory. Defaults to audio folder in this project.
\t\tIf output folder does not exist, creates it.
\n
\t-h, --help
\t\tPrint help and exit.
\n
Examples:
\tCreate Dutch MP3s using mydutchtext.txt.
\tThe files will be stored in mydir, with names matching the word translated.
\n
\t\t> fetch_audio.sh -d mydir -i wordlist.txt
\n
Requirements:
\t* Google TTS cli
\t* Text file to convert to MP3, one word per line.
"

OUTPUT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}";)" &> /dev/null && pwd 2> /dev/null;)"
WORDLIST_LANGUAGE="nl"
WORDLIST_FILE="${OUTPUT_DIR}/../top-10000-dutch-words.txt"

fetch_audio_files() {
    if [ "0" -eq "${#WORDLIST_FILE}" ]; then
        echo -e "$USAGE"
        exit 0
    fi

    if [ ! -f "$WORDLIST_FILE" ]; then
        echo "ERROR: transcript file ${WORDLIST_FILE} not found."
        echo "Please create a text file to transcribe to MP3."
        echo "The transcript should have one sentence per line."
        exit 1
    fi

    if [ ! -d "$OUTPUT_DIR" ]; then
        echo "Output dir ${OUTPUT_DIR} does not exist. Creating..."
        mkdir $OUTPUT_DIR
    fi

    if [ "${#OUTPUT_FILENAME}" -gt "0" ]; then
        OUTPUT_FILENAME="${OUTPUT_FILENAME}-"
    fi

    readarray -t transcript < $WORDLIST_FILE
    counter=1
    for line in "${transcript[@]}"; do
        if [ "$counter" -gt "100" ]; then
            echo "Processed 100 entries. Pausing to prevent spamming server."
            sleep 5m
            counter=1
        fi

        output_file="${OUTPUT_DIR}/../audio/${line}.mp3"
        if [ ! -f "$output_file" ]; then
            gtts-cli "$line" -l "${WORDLIST_LANGUAGE}" -o "$output_file"
            sleep 0.30
            echo "${counter} Created $output_file"
            counter=$(( counter+1 ))
        else
            echo "${output_file} file already exists. Skipping."
        fi
    done
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        -d|--dir)
            OUTPUT_DIR="$2"
            shift
            shift
            ;;
        -h|--help)
            echo -e $USAGE
            exit 0
            ;;
        -i|--input_file)
            WORDLIST_FILE="$1"
            shift
            shift
            ;;
        *)
            echo -e "$USAGE"
            exit 0
            ;;
    esac
done

fetch_audio_files
