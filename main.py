from flask import Flask, render_template, request, redirect
from pytube import YouTube
import requests, urllib.parse, re
from liblitetube import *

def get_related(video):
    search = Search(video.title+" "+video.author)
    search_results = search['results']
    return(search_results)

app = Flask(__name__, template_folder='templates', static_url_path='/static', static_folder='static')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/watch/<video_id>")
def watch(video_id):
    youtube_url = 'https://www.youtube.com/watch?v='+video_id
    try:
        video = YouTube(youtube_url)
        video_url = video.streams.get_highest_resolution().url
        data = get_related(video)
        return render_template('watch.html', video_url=video_url, video=video, data=data)
    except Exception as e:
        return str(e)

@app.route('/channel/<channel_name>')
def channel(channel_name):
    if request.args.get("token") and request.args.get("key"):
        data = ChannelLoadPage(request.args.get("token"), request.args.get("key"))
        return(data)
    c = get_channel_data(channel_name)
    print(c["continuationtoken"])
    return render_template('channel.html', channel=c, videos=c['videos'], human_format=human_format)

@app.route('/c/<channelname>')
def channel_c(channelname):
    data = get_canonical_link(channelname).replace("https://www.youtube.com", "")
    return redirect(data, code=302)

@app.route("/search")
def search():
    query = request.args.get("q")
    if not query:
        return "Please enter a search query!"
    try:
        if request.args.get("token") and request.args.get("key"):
            data = SearchLoadPage(request.args.get("token"), request.args.get("key"))
            return(data)
        search = Search(query)
        search_results = search['results']
        return render_template("search.html", search_results=search_results, key=search["key"], token=search["continuationtoken"], query=query, human_format=human_format)
    except Exception as e:
        print(e)
        return "error"

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
