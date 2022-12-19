# Playlist-Pro-Users
# How to run server
1. Install requirements: `pip install -r requirements.txt`
2. Start server: `python .\src\application.py`

# How to run server on EC2
1. Go to the ec2 instance and pull code -> pkill -9 python -> cd src -> source env.sh -> nohup python3 -m application &