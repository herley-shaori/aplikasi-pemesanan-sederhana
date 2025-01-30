#!/bin/bash

# Check if Streamlit is running
if ps aux | grep -v grep | grep streamlit > /dev/null
then
    echo "Streamlit is running."
else
    echo "Streamlit is NOT running."
    exit 1
fi

# Check if the application is accessible
if curl -s --head http://localhost:8501 | grep "200 OK" > /dev/null
then
    echo "Streamlit app is accessible."
else
    echo "Streamlit app is NOT accessible."
    exit 1
fi

echo "Streamlit app is running successfully."
exit 0