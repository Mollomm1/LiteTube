import json, datetime, yt_dlp, timeago

def GetTracks(video):
    data = {}
    streams = {}
    itags = []

    ydl = yt_dlp.YoutubeDL({'quiet': True})
    info = json.loads(json.dumps(ydl.sanitize_info(ydl.extract_info('https://youtube.com/watch?v='+video, download=False))))
    allstreams = info["formats"]

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
    print(data["upload_date"])
    data["description"] = info["description"]
    data["channel_follower_count"] = info["channel_follower_count"]
    data["like_count"] = info["like_count"]
    data["thumbnail"] = info["thumbnail"]

    # regular 16:9

    for i in allstreams:
        itags.append(i["format_id"])

    if "18" in itags:
        streams["360p"] = []
        for o in allstreams:
            if o["format_id"] == "18":
                streams["360p"].append({"size": "360", "url": o['url']})

    if "22" in itags:
        streams["720p"] = []
        for o in allstreams:
            if o["format_id"] == "22":
                streams["720p"].append({"size": "720", "url": o['url']})

    '''
    if ("250" and "248") in itags:
        streams["1080p"] = []
        for o in allstreams:
            if o["format_id"] == "250":
                streams["1080p"].append({"type": "audio/webm", "url": o['url']})
            if o["format_id"] == "248":
                streams["1080p"].append({"type": "video/webm", "url": o['url']})
    
    if ("250" and "303") in itags:
        streams["1080p60"] = []
        for o in allstreams:
            if o["format_id"] == "250":
                print("hi")
                streams["1080p60"].append({"type": "audio/webm", "url": o['url']})
            if o["format_id"] == "303":
                print("hi")
                streams["1080p60"].append({"type": "video/webm", "url": o['url']})

    if ("250" and "308") in itags:
        streams["1440p60"] = []
        for o in allstreams:
            if o["format_id"] == "250":
                streams["1440p60"].append({"type": "audio/webm", "url": o['url']})
            if o["format_id"] == "308":
                streams["1440p60"].append({"type": "video/webm", "url": o['url']})

    if ("250" and "315") in itags:
        streams["2160p60"] = []
        for o in allstreams:
            if o["format_id"] == "250":
                streams["2160p60"].append({"type": "audio/webm", "url": o['url']})
            if o["format_id"] == "315":
                streams["2160p60"].append({"type": "video/webm", "url": o['url']})
    '''

    data["streams"] = streams
    return(data)