### Blackboard assignment autodownloader

To use this program I recommend you create a copy of your firefox profile and use that copy for this program. This way you don't mess with your main firefox profile. The reason we want this is to keep any cookies and sessions so you are automatically logged in to blackboard.

To do this:
```
cp -r ~/.mozilla/firefox/<some random string like abcd1234>.default-release ~/.mozilla/firefox/selenium-profile
```

To run the program:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python blackboard_downloader.py --profile-path ~/.mozilla/firefox/selenium-profile
```