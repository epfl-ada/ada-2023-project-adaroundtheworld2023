#!/bin/bash

# constants
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"
FILE_ID=""  # TODO: update
DATA_PATH="$ROOT_DIR/data"
FILENAME="graph_data.zip"

# download the file
cd "$DATA_PATH"
gdown "$FILE_ID"

# extract the main zip file and remove zip itself
unzip -q "$DATA_PATH/$FILENAME" -d "$DATA_PATH"
rm "$DATA_PATH/$FILENAME"

echo "Extraction complete"