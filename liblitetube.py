import requests, urllib.parse, re, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'TE': 'Trailers',
}

cookies = {
    'CONSENT': 'YES+cb.20210328-17-p0.en-GB+FX+181',
}

def human_format(num):
    magnitude = 0
    try:
        num = int("".join([ele for ele in num if ele.isdigit()]))
        while abs(int(num)) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '%.2f%s' % (int(num), ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
    except Exception:
        return '?'

def get_canonical_link(channel_url):
    r = requests.get("https://www.youtube.com/"+channel_url, headers=headers, cookies=cookies)
    
    start_index = r.text.find('<link rel="canonical" href="') + len('<link rel="canonical" href="')
    end_index = r.text.find('"', start_index)
    if start_index != -1 and end_index != -1:
        return r.text[start_index:end_index]
    else:
        return None

def get_channel_data(channel_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.5',
        'content-encoding': 'gzip',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    }

    r = requests.get("https://www.youtube.com/channel/"+channel_url+"/videos", headers=headers, cookies=cookies)
    channeldata_metadata = json.loads(r.text.split("var ytInitialData = ")[1].split("</script>")[0][:-1])["metadata"]["channelMetadataRenderer"]
    channeldata_header = json.loads(r.text.split("var ytInitialData = ")[1].split("</script>")[0][:-1])["header"]["c4TabbedHeaderRenderer"]
    channeldata = {}
    channeldata["channel_name"] = channeldata_metadata["title"]
    try:
        channeldata["channel_profile_picture"] = channeldata_metadata["avatar"]["thumbnails"][0]
    except Exception:
        channeldata["channel_profile_picture"] = ""
    try:
        channeldata["channel_banner"] = channeldata_header["banner"]["thumbnails"][-1]
    except Exception:
        channeldata["channel_banner"] = ""
    try:
        channeldata["channel_description"] = channeldata_metadata["description"]
    except Exception:
        channeldata["channel_description"] = ""
    
    try:
        if channeldata_header["badges"][0]["metadataBadgeRenderer"]["tooltip"] == "Verified":
            channeldata["isVerified"] = True
        else:
            channeldata["isVerified"] = False
    except Exception:
        channeldata["isVerified"] = False
    channeldata["videos"] = []
    
    for i in json.loads(r.text.split("var ytInitialData = ")[1].split("</script>")[0][:-1])["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][1]["tabRenderer"]["content"]["richGridRenderer"]["contents"]:
        video_data = {}
        try:
            video_data["id"] = i["richItemRenderer"]["content"]["videoRenderer"]["videoId"]
            video_data["views"] = human_format(i["richItemRenderer"]["content"]["videoRenderer"]["viewCountText"]["simpleText"])
            video_data["published"] = i["richItemRenderer"]["content"]["videoRenderer"]["publishedTimeText"]["simpleText"]
            video_data["thumbnail"] = i["richItemRenderer"]["content"]["videoRenderer"]["thumbnail"]["thumbnails"][0]["url"]
            video_data["title"] = i["richItemRenderer"]["content"]["videoRenderer"]["title"]["runs"][0]["text"]
            channeldata["videos"].append(video_data)
        except Exception:
            del(video_data)
    channeldata["key"] = str(r.text.split('"INNERTUBE_API_KEY":"')[1].split('"')[0])
    try:
        channeldata["continuationtoken"] = str(r.text.split('{"sendPost":true,"apiUrl":"/youtubei/v1/browse"}},"continuationCommand":{"token":"')[1].split('"')[0])
    except Exception:
        channeldata["continuationtoken"] = None
    return(channeldata)

def ChannelLoadPage(continuation_token, key):
    lpheaders = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0,gzip(gfe)',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-type': 'application/json',
        'Accept': 'text/plain',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    } # use his own headers

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

    url = f"https://www.youtube.com/youtubei/v1/browse?key={key}"
    response = requests.post(url, json=body, headers=lpheaders, cookies=cookies)
    #with open("file.txt", "w") as file:
    #    print(file.write(response.text))
    results = []
    try:
        video_contents = response.json()["onResponseReceivedActions"][1]["reloadContinuationItemsCommand"]["continuationItems"]
    except Exception:
        video_contents = response.json()["onResponseReceivedActions"][0]["appendContinuationItemsAction"]["continuationItems"]
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
        except KeyError as e:
            print(e)
            pass
    data = {}
    try:
        data["token"] = response.json()["onResponseReceivedActions"][1]["reloadContinuationItemsCommand"]["continuationItems"][-1]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
    except Exception:
        try:
            data["token"] = response.json()["onResponseReceivedActions"][0]["appendContinuationItemsAction"]["continuationItems"][-1]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
        except Exception:
            data["token"] = None
    data["videos"] = results
    return(data)

def SearchLoadPage(continuation_token, key):
    lpheaders = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0,gzip(gfe)',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-type': 'application/json',
        'Accept': 'text/plain',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    } # use his own headers

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

    url = f"https://www.youtube.com/youtubei/v1/search?key={key}"
    response = requests.post(url, json=body, headers=lpheaders, cookies=cookies)
    results = []
    video_contents = response.json()["onResponseReceivedCommands"][0]["appendContinuationItemsAction"]["continuationItems"][0]["itemSectionRenderer"]["contents"]
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
    data = {}
    data["token"] = response.json()["onResponseReceivedCommands"][0]["appendContinuationItemsAction"]["continuationItems"][1]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
    data["videos"] = results
    return(data)

def Search(query):
    response = requests.get("https://www.youtube.com/results", headers=headers, cookies=cookies, params={"search_query": query})
    response.raise_for_status()
    response_content = response.content.decode("utf-8")

    data = {}
    results = []

    initial_data_start = 'var ytInitialData = '
    initial_data_end = ';</script>'
    initial_data_start_idx = response_content.find(initial_data_start) + len(initial_data_start)
    initial_data_end_idx = response_content.find(initial_data_end, initial_data_start_idx)

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
    data["results"] = results
    return data