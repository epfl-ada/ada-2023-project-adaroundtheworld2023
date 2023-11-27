#!/bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

cd "$ROOT_DIR/data/embeddings/similarities/"

# define ID-s in Google Drive
declare -A hashtable
hashtable['1900']='1Jjh1bkzJc2Fok-A-DAb0lRL2NnfNFlhc'
hashtable['1910']='15rgicexDDSbKQq-FEnbNSpf8R1TOox57'
hashtable['1920']='1zlRGYhpWIUPn1sQ3XFnbcqB0F31VIUzI'
hashtable['1930']='1nnvWla2bSx9jE-zTO47WVPpBkIJ4v7zG'
hashtable['1940']='125LT50XpcU4xyGTwrkghi-OdJHq_7_Sw'
hashtable['1950']='1Y3pvCKHljKLXhGdvTO0dCje7DaPMqIJd'
hashtable['1960']='1KJwUsXVwK1acukCqCz1N4ddg-P0eMPNR'
hashtable['1970']='1iU4Jda9ptOzGVimg54GVEgKDNP8KwCMR'
hashtable['1980']='1h9cE3e6pO9892kmSpI9XMa4zXPkFSuSO'
hashtable['1990']='1UJcsbPQI2hAqYJW483fK-ML89jp8paGO'
hashtable['2000']='1nYRmcdqg8c_uuDutAE1LmPmT4Iok6ioL'
hashtable['2010']='1v0hZ-X0pLA-cQk1X6bhwByICjyHjjk5P'

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
