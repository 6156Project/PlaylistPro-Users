# Playlist-Pro-Users
# How to run server
1. Install requirements: `pip install -r requirements.txt`
2. Start server: `python .\src\application.py`

# How to run server on EC2
1. Go to the ec2 instance and pull code -> pkill -9 python -> cd src -> source env.sh -> nohup python3 -m application &

# ssh
1.  ssh -o StrictHostKeyChecking=no -i "user.pem" ec2-user@ec2-52-90-71-19.compute-1.amazonaws.com

