#!/bin/bash

# Function to greet a user
greet_user() {
    echo "Hello, $1!"
}

# Loop through a list of names
for name in Alice Bob Charlie
do
    greet_user $name
done
