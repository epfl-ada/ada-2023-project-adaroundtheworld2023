#!/bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

cd "$ROOT_DIR/data/embeddings/plots/"

# define ID-s in Google Drive
declare -A hashtable
hashtable['1900']='1VvekfRnMyDPtg-mPTW65JtRZy2qETCQ-'
hashtable['1910']='1FU6RFLCYCD4iIvXiarLGgdzMQEFcRqSD'
hashtable['1920']='148Fp5lSwl0kflMkpiSvwziKJyGR_wBft'
hashtable['1930']='16g85xfwVfp9whD1c0XqeztcuMlqEjUdO'
hashtable['1940']='1Wm9GuCJ1sp9WNY1xXROQcCc6mbz3cBR5'
hashtable['1950']='1tRm-M_ALdE245hxoHeffNQyceX93ZDU4'
hashtable['1960']='1t7hqyIdxAD4Uvyiv76a9m_IlulJn0VdO'
hashtable['1970']='100FgJq8JHUX0NdkB7-2mYM6FpPuG92xZ'
hashtable['1980']='1c1n8aWHe4aXlXr7g9uNtF5GJ9wVo6E2m'
hashtable['1990']='1m3rxSOEhUBH4heL9b3sFsW0584xImqVP'
hashtable['2000']='176eCC8W6ecfNYsD-N07vKKwXK9h1L3re'
hashtable['2010']='1IQaIsTCaPO5QWxfYrpMVWmKrZuz5OSo9'

# if no arguments passed -> download all files
if [ "$*" == "" ]; then
    echo "No arguments provided, downloading all files."
    for key in "${!hashtable[@]}"; do
        gdown "${hashtable[$key]}"
    done

# if arguments passed -> download specified files
else
    for key in "$@"; do
        gdown "${hashtable[$key]}"
    done
fi

echo "Extraction complete"
