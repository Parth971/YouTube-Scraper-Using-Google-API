from googleapiclient.discovery import build
import json
import requests
import re
from time import time
from dotenv import load_dotenv
import os

load_dotenv()


class Non200ResponseException(Exception):
    """
    Exception raised when a non-200 HTTP response is received.

    Attributes:
        response: The response object that triggered the exception.
        status_code: The status code of the non-200 response.
        message: A formatted message describing the exception.
    """

    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
        self.message = f"Received a non-200 HTTP response: {self.status_code}"
        super().__init__(self.message)


class APIKeyNotFoundException(Exception):
    """
    Exception raised when the API key (INNERTUBE_API_KEY) is not found.

    Attributes:
        message: A custom message describing the exception.
    """

    def __init__(self, message="INNERTUBE_API_KEY not found."):
        """
        Initialize the exception.

        Args:
            message: A custom message describing the exception.
        """
        self.message = message
        super().__init__(self.message)


class YouTubeAPI:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.channel_name = None

    def scrap(self, channel_name):
        """
        Scrapes data from a YouTube channel.

        Args:
            channel_name (str): The name of the YouTube channel.

        Raises:
            Non200ResponseException: If a non-200 HTTP response is received.

        Prints:
            Information about the scraping progress or any error that occurred.
        """
        try:
            self.channel_name = channel_name

            print('Getting channel Id...')
            response = requests.get(
                url=f'https://www.youtube.com/@{channel_name}/'
            )
            if response.status_code != 200:
                raise Non200ResponseException(response)

            channel_id = self.get_channel_id(response.text)

            self.fetch(channel_id)

            print(f'\n{"#" * 20} Completed {"#" * 20}')
        except Exception as e:
            print('Error occurred')
            print(e)

    def get_channel_id(self, response_text):
        """
        Extracts channel Id from channel's main page of YouTube

        Args:
            response_text (str): The text of the HTTP response.

        Returns:
            str: The extracted channel ID.

        Prints:
            The extracted channel ID.

        """
        pattern = r'channel_id=([^"]+)'
        match = re.search(pattern, response_text)
        if match:
            json_value = match.group(1)
            print(f'Channel ID: {json_value}')
            return json_value

        raise APIKeyNotFoundException()

    def fetch(self, channel_id):
        """
        Fetches the videos from the specified YouTube channel.

        Args:
            channel_id (str): The ID of the YouTube channel.

        Prints:
            The progress of fetching the videos.
            A completion message when fetching is completed.

        """
        channel_content = self.youtube.channels().list(
            part='contentDetails', id=channel_id
        ).execute()

        playlist_id = channel_content['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        videos = []
        next_page_token = None

        print('\nFetching...')
        while True:
            # Fetch the playlistItems (the videos)
            res = self.youtube.playlistItems().list(
                playlistId=playlist_id,
                part='snippet',
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            videos += res['items']
            next_page_token = res.get('nextPageToken')

            if next_page_token is None:
                print('Completed fetching')
                break

        self.save(videos)

    def save(self, videos):
        """
        Saves the fetched video links to a JSON file.

        Args:
            videos (list): A list of video objects containing the fetched videos.

        Prints:
            The number of video links being saved.
            
        Writes:
            A JSON file named "{channel_name}.json" with the following structure:
            {
                "count": <count>,
                "links": [
                    "https://www.youtube.com/watch?v=<video_id_1>",
                    "https://www.youtube.com/watch?v=<video_id_2>",
                    ...
                ]
            }

        """
        count = len(videos)
        print(f'\nSaving {count} links...')
        with open(f"{self.channel_name}.json", 'w') as fp:
            data = {
                'count': count,
                'links': [
                    f"https://www.youtube.com/watch?v={video['snippet']['resourceId']['videoId']}"
                    for video in videos
                ]
            }
            json.dump(data, fp, indent=4)


if __name__ == '__main__':
    """
    Entry point of the script.

    Fetches and saves videos from a YouTube channel.

    Environment Variables:
        YOUTUBE_API_KEY (str): The API key for accessing the YouTube Data API.

    Prints:
        The total execution time of the script.

    """

    api_key = os.environ.get('YOUTUBE_API_KEY')
    channel_name = 'thenewboston'

    start_time = time()

    YouTubeAPI(api_key).scrap(channel_name)

    print(f'\nTotal time: {time() - start_time} sec')
