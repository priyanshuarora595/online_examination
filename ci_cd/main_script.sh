cd ..
source ~/.virtualenvs/online-exam/bin/activate
git stash -u
git pull origin main
git stash pop
pip install -r requirements.txt