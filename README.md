

## Install Virtual Environment

Installing python pakages in virtual environment is recommended.

Install [Python Virtual Environment](https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/)


## Install requirements.txt

After your virtual environment is activated, run command

    pip install -r requirements.txt


## Setup Google Accoount And Generate API

Follow steps from [here](https://developers.google.com/youtube/v3/quickstart/python#step_1_set_up_your_project_and_credentials)

#### Note: make sure the YouTube API is enabled for your project (in google cloud).


## Create .env file
Add api variable and set its value from generated API

    YOUTUBE_API_KEY=your api key


## To Run YouTube Scraper

    python main.py

#### Note: To add channel name, open `main.py` file, scroll to the bottom of file and change value of variable

    channel_name = 'thenewboston' # Name of @channel

After script run successfully, their will be file generated named `channel_name.json` which contains all the videos link.
