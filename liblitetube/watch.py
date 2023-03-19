# Import necessary libraries
import json
import datetime
import yt_dlp
import timeago

def GetTracks(video):
    """
    Function to get tracks from a YouTube video
    """
    # Initialize empty dictionaries and lists
    data = {}
    streams = {}
    itags = []

    # Set up YouTube downloader with quiet mode enabled
    ydl = yt_dlp.YoutubeDL({'quiet': True})

    # Extract information about the video using the downloader
    info = json.loads(json.dumps(ydl.sanitize_info(ydl.extract_info('https://youtube.com/watch?v='+video, download=False))))
    allstreams = info["formats"]

    # Extract relevant information from the video information
    data["channel_id"] = info["channel_id"]
    data["title"] = info["fulltitle"]
    data["view_count"] = info["view_count"]
    data["uploader"] = info["uploader"]
    data["age_limit"] = info["age_limit"]
    a = info["upload_date"]
    date_year = int(str(a)[0:4])
    date_month = int(str(a)[4:6])
    date_day = int(str(a)[6:8])
    data["upload_date"] = timeago.format(datetime.date(date_year, date_month, date_day))
    data["description"] = info["description"]
    data["channel_follower_count"] = info["channel_follower_count"]
    data["like_count"] = info["like_count"]
    data["thumbnail"] = info["thumbnail"]

    # Extract available video streams
    for i in allstreams:
        itags.append(i["format_id"])

    # Extract 360p stream if available
    if "18" in itags:
        streams["360p"] = []
        for o in allstreams:
            if o["format_id"] == "18":
                streams["360p"].append({"size": "360", "url": o['url']})

    # Extract 720p stream if available
    if "22" in itags:
        streams["720p"] = []
        for o in allstreams:
            if o["format_id"] == "22":
                streams["720p"].append({"size": "720", "url": o['url']})
    
    # Add streams to data dictionary and return
    data["streams"] = streams
    return(data)