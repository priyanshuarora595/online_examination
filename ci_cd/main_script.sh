# cd ..
pwd
if [[ -z "$VIRTUAL_ENV" ]]; then
    source ~/.virtualenvs/online-exam/bin/activate
else
    echo "Already in virtual environment: $VIRTUAL_ENV"
fi

git stash -u
git pull origin main
git stash drop
pip install -r requirements.txt