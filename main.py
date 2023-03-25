# importing the necessary libraries and modules
from flask import Flask, render_template, request, redirect, Response
from waitress import serve
import requests
import urllib.parse
import re
from liblitetube.main import *

# change variables here
host="0.0.0.0"
port=5000

def get_related(video):
    '''
    A function to get related videos for a given video
    '''
    search = Search(video["title"]+" "+video["uploader"])
    search_results = search['results']
    return(search_results)

app = Flask(__name__, template_folder='templates', static_url_path='/static', static_folder='static')

@app.route("/")
def index():
    '''
    The root endpoint of the app
    '''
    return render_template("index.html")

'''
errors pages
'''
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html', e=e), 500
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404
'''

'''

@app.route("/watch/<video_id>")
def _watch(video_id):
    '''
    The endpoint for watching a video
    '''
    video = GetTracks(video_id)
    streams = video["streams"]
    data = get_related(video)
    return render_template('watch.html', streams=streams, video=video, data=data, video_id=video_id)

@app.route('/channelicon/<channel_name>')
def channelicon(channel_name):
    '''
    An endpoint for fetching the channel icon
    '''
    c = get_channel_data(channel_name)
    resp = requests.get(c['channel_profile_picture']['url'])
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in     resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response

@app.route('/channel/<channel_name>')
def channel(channel_name):
    '''
    An endpoint for displaying a channel's data
    '''
    if request.args.get("token") and request.args.get("key"):
        try:
            data = ChannelLoadPage(request.args.get("token"), request.args.get("key"))
        except requests.exceptions.HTTPError:
            data = "end"
        return(data)
    c = get_channel_data(channel_name)
    return render_template('channel.html', channel=c, videos=c['videos'], human_format=human_format)

@app.route('/c/<channelname>')
def channel_c(channelname):
    '''
    An endpoint for redirecting to the canonical link for a channel
    '''
    data = get_canonical_link(channelname).replace("https://www.youtube.com", "")
    return redirect(data, code=302)

@app.route("/search")
def search():
    '''
    An endpoint for searching for videos
    '''
    query = request.args.get("q")
    if not query:
        return "Please enter a search query!"
    if request.args.get("token") and request.args.get("key"):
        try:
            data = SearchLoadPage(request.args.get("token"), request.args.get("key"))
        except requests.exceptions.HTTPError:
            data = "end"
        return(data)
    search = Search(query)
    search_results = search['results']
    return render_template("search.html", search_results=search_results, key=search["key"], token=search["continuationtoken"], query=query, human_format=human_format)

if __name__ == "__main__":
    '''
    Main thread that start the app
    '''
    print(f'LiteTube is listening on http://{host}:{port}')
    serve(app, host=host, port=port)
    # use this for dev: app.run(debug=True, threaded=True, host=host, port=port)