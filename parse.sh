#!/bin/bash

# Check if the number of arguments is correct
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file_name>"
    exit 1
fi

# Assign the file name to a variable
file_name="$1"

# Run the lexer.py script with the file name
python lexer.py "$file_name"

# Check if the lexer.py script executed successfully
if [ $? -ne 0 ]; then
    echo "Lexing failed."
    exit 2
fi

# Run the wwl_parser.py script
python wwl_parser.py testfile.txt

# Check if the wwl_parser.py script executed successfully
if [ $? -ne 0 ]; then
    echo "Error: parsing failed."
    exit 3
fi
echo "Parsing was successful."