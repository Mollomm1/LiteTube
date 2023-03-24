# Import necessary libraries
import requests
import urllib.parse
import re
import json
from . lt_misc import *

def SearchLoadPage(continuation_token, key):
    """
    Function to load and return search results page (to continue pagination)
    """
    lpheaders = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0,gzip(gfe)',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-type': 'application/json',
        'Accept': 'text/plain',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    }

    body = {
        "context": {
            "client": {
                "hl": "en",
                "gl": "US",
                "remoteHost": "",
                "deviceMake": "",
                "deviceModel": "",
                "visitorData": "",
                "userAgent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0,gzip(gfe)",
                "clientName": "WEB",
                "clientVersion": "2.20230309.08.00",
                "osName": "X11",
                "osVersion": "",
                "originalUrl": "https://www.youtube.com/results?search_query=bruh",
                "platform": "DESKTOP",
                "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                "configInfo": {
                    "appInstallData": ""
                },
                "userInterfaceTheme": "USER_INTERFACE_THEME_DARK",
                "timeZone": "",
                "browserName": "",
                "browserVersion": "",
                "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "deviceExperimentId": "",
                "screenWidthPoints": 0,
                "screenHeightPoints": 0,
                "screenPixelDensity": 0,
                "screenDensityFloat": 0,
                "utcOffsetMinutes": 60,
                "mainAppWebInfo": {
                    "graftUrl": "https://www.youtube.com/results?search_query=bruh",
                    "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                    "isWebNativeShareAvailable": False
                }
            },
            "user": {
                "lockedSafetyMode": False
            },
            "request": {
                "useSsl": True,
                "internalExperimentFlags": [],
                "consistencyTokenJars": []
            },
            "clickTracking": {
                "clickTrackingParams": ""
            },
            "adSignalsInfo": {
                "params": []
            }
        },
        "continuation": str(continuation_token)
    }

    # Initialize empty dictionaries and lists
    results = []
    data = {}

    # Send request to get the page content
    url = f"https://www.youtube.com/youtubei/v1/search?key={key}"
    response = requests.post(url, json=body, headers=lpheaders, cookies=cookies)

    # Extract the required data to extract videos
    video_contents = response.json()["onResponseReceivedCommands"][0]["appendContinuationItemsAction"]["continuationItems"][0]["itemSectionRenderer"]["contents"]

    # Extract data about the videos
    for video in video_contents:
        try:
            video_data = {
                "id": video["videoRenderer"]["videoId"],
                "views": human_format(video["videoRenderer"]["viewCountText"]["simpleText"]),
                "published": video["videoRenderer"]["publishedTimeText"]["simpleText"],
                "thumbnail": video["videoRenderer"]["thumbnail"]["thumbnails"][0]["url"],
                "title": video["videoRenderer"]["title"]["runs"][0]["text"],
                "channel": video["videoRenderer"]["longBylineText"]["runs"][0]["text"],
                "owner_url": video["videoRenderer"]["ownerText"]["runs"][0]["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]
            }
            results.append(video_data)
        except KeyError:
            pass
    
    # Extract the key and continuation token for pagination
    data["token"] = response.json()["onResponseReceivedCommands"][0]["appendContinuationItemsAction"]["continuationItems"][1]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
    
    # Add streams to data dictionary and return
    data["videos"] = results
    return(data)

def Search(query):
    """
    Function to load and return search results page
    """
    
    # Initialize empty dictionaries and lists
    data = {}
    results = []

    # Send request to get the page content
    response = requests.get("https://www.youtube.com/results", headers=headers, cookies=cookies, params={"search_query": query})
    response.raise_for_status()
    response_content = response.content.decode("utf-8")

    # Extract the required data
    initial_data_start = 'var ytInitialData = '
    initial_data_end = ';</script>'
    initial_data_start_idx = response_content.find(initial_data_start) + len(initial_data_start)
    initial_data_end_idx = response_content.find(initial_data_end, initial_data_start_idx)

    # Extract data about the videos
    try:
        initial_data = json.loads(response_content[initial_data_start_idx:initial_data_end_idx])
        video_contents = initial_data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']

        for video in video_contents:
            try:
                video_data = {
                    "id": video["videoRenderer"]["videoId"],
                    "views": video["videoRenderer"]["viewCountText"]["simpleText"],
                    "published": video["videoRenderer"]["publishedTimeText"]["simpleText"],
                    "thumbnail": video["videoRenderer"]["thumbnail"]["thumbnails"][0]["url"],
                    "title": video["videoRenderer"]["title"]["runs"][0]["text"],
                    "channel": video["videoRenderer"]["longBylineText"]["runs"][0]["text"],
                    "owner_url": video["videoRenderer"]["ownerText"]["runs"][0]["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]
                }
                results.append(video_data)
            except KeyError:
                pass

        data["key"] = str(response.text.split('"INNERTUBE_API_KEY":"')[1].split('"')[0])
        data["continuationtoken"] = str(response.text.split('"commandMetadata":{"webCommandMetadata":{"sendPost":true,"apiUrl":"/youtubei/v1/search"}},"continuationCommand":{"token":"')[-1].split('"')[0])
    except (ValueError, KeyError):
        pass

    # Add search results to data dictionary and return
    data["results"] = results
    return data