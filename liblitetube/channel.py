# Import necessary libraries
import json
import re
import urllib.parse
import requests
from .lt_misc import *

def get_channel_data(channel_url):
    """
    This function extracts data about a YouTube channel
    """
    # Send request to get the page content
    url = f"https://www.youtube.com/channel/{channel_url}/videos"
    r = requests.get(url, headers=headers, cookies=cookies)
    r.raise_for_status()

    # Extract the required data from the page
    page_data = json.loads(re.search(r"ytInitialData\s*=\s*({.*?});", r.text).group(1))
    channeldata_metadata = page_data["metadata"]["channelMetadataRenderer"]
    channeldata_header = page_data["header"]["c4TabbedHeaderRenderer"]

    # Store the extracted data in a dictionary
    channeldata = {
        "channel_name": channeldata_metadata["title"],
        "subscriberCount": channeldata_header["subscriberCountText"]["simpleText"],
        "videosCount": channeldata_header["videosCountText"]["runs"][0]["text"],
        "channel_profile_picture": channeldata_metadata["avatar"]["thumbnails"][0] if "avatar" in channeldata_metadata else "",
        "channel_banner": channeldata_header["banner"]["thumbnails"][-1] if "banner" in channeldata_header else "",
        "channel_description": channeldata_metadata.get("description", ""),
        "isVerified": channeldata_header["badges"][0]["metadataBadgeRenderer"]["tooltip"] == "Verified" if channeldata_header.get("badges") else False,
        "videos": []
    }

    # Extract data about the videos
    try:
        for video in page_data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][1]["tabRenderer"]["content"]["richGridRenderer"]["contents"]:
            try:
                video_data = {
                    "id": video["richItemRenderer"]["content"]["videoRenderer"]["videoId"],
                    "views": human_format(video["richItemRenderer"]["content"]["videoRenderer"]["viewCountText"]["simpleText"]),
                    "published": video["richItemRenderer"]["content"]["videoRenderer"]["publishedTimeText"]["simpleText"],
                    "thumbnail": video["richItemRenderer"]["content"]["videoRenderer"]["thumbnail"]["thumbnails"][0]["url"],
                    "title": video["richItemRenderer"]["content"]["videoRenderer"]["title"]["runs"][0]["text"],
                }
                channeldata["videos"].append(video_data)
            except KeyError:
                pass

        # Extract the key and continuation token for pagination
        try:
            channeldata["key"] = re.search(r'"INNERTUBE_API_KEY":"(.*?)"', r.text).group(1)
        except AttributeError:
            channeldata["key"] = None

        try:
            channeldata["continuationtoken"] = re.search(r'"continuationCommand":{"token":"(.*?)"', r.text).group(1)
        except AttributeError:
            channeldata["continuationtoken"] = None
    except Exception:
        return channeldata
    return channeldata

def ChannelLoadPage(continuation_token, key):
    """
    This function extracts data about a YouTube content, it load next page stuff.
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
    url = f"https://www.youtube.com/youtubei/v1/browse?key={key}"
    r = requests.post(url, json=body, headers=lpheaders, cookies=cookies)
    r.raise_for_status()

    # Extract the required data to extract videos
    try:
        video_contents = r.json()["onResponseReceivedActions"][1]["reloadContinuationItemsCommand"]["continuationItems"]
    except Exception:
        video_contents = r.json()["onResponseReceivedActions"][0]["appendContinuationItemsAction"]["continuationItems"]
    
    # Extract data about the videos
    for video in video_contents:
        try:
            video_data = {
                "id": video["richItemRenderer"]["content"]["videoRenderer"]["videoId"],
                "views": human_format(video["richItemRenderer"]["content"]["videoRenderer"]["viewCountText"]["simpleText"]),
                "published": video["richItemRenderer"]["content"]["videoRenderer"]["publishedTimeText"]["simpleText"],
                "thumbnail": video["richItemRenderer"]["content"]["videoRenderer"]["thumbnail"]["thumbnails"][0]["url"],
                "title": video["richItemRenderer"]["content"]["videoRenderer"]["title"]["runs"][0]["text"]
            }
            results.append(video_data)
        except KeyError:
            pass

    # Extract the key and continuation token for pagination
    try:
        data["token"] = r.json()["onResponseReceivedActions"][1]["reloadContinuationItemsCommand"]["continuationItems"][-1]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
    except Exception:
        try:
            data["token"] = r.json()["onResponseReceivedActions"][0]["appendContinuationItemsAction"]["continuationItems"][-1]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
        except Exception:
            data["token"] = None
    
    # Add videos to data dictionary and return
    data["videos"] = results
    return(data)