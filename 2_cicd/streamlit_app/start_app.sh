#!/bin/bash
echo "Current directory: $(pwd)"
echo "Contents of /home/ec2-user/streamlit-app:"
ls -l /home/ec2-user/streamlit-app
cd /home/ec2-user/streamlit-app
nohup streamlit run main.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
sleep 10
exit 0