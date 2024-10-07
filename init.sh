cd /home/ubuntu
mkdir v0
cd v0

# Install Deps
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip certbot net-tools

# TODO: Pull Git Repo
git config --global user.email "araadshams2003@gmail.com"
git config --global user.name "Araad Shams"
git clone https://github.com/cumuless/api.git .
git checkout origin/demo

python3 -m venv venv
source ./venv/bin/activate
pip install boto3 Flask flask_cors python-dotenv flask_cognito cognitojwt marshmallow uuid

# SSL Cert
# sudo certbot certonly --standalone -d api.cumuless.com

# Nginx Config
sudo apt-get install python3-certbot-nginx nginx
sudo cp nginx.conf /etc/nginx/sites-enabled/server
sudo nginx -t
sudo systemctl reload nginx

# TODO: Start Server

echo "Done! Enter run the following in your terminal: "

source ./venv/bin/activate
pm2 start main.py