from flask import render_template, Flask, jsonify, redirect, request, url_for, send_file
import bs
import bs2
import os
import glob
from construction import get_songs_msgs, get_instruments, play_song_or_save, programs_for_names
from probabilities import get_channels_dict
import uuid

app = Flask(__name__)
all_mid = []

"""
current issues:

when you click update, it re-renders every checkbox, hence clearing all selected checkboxes. also different order potentially
we are redownloading files we already have since i took a simplistic approach of clearing the folder then just downloading all of the songs that are currently selected
we allow duplicate songs (server side and client side). do we? wont it just replace itself in the dict
the code relies on the name of the song being different
we don't check and update previousresults to only contain previous results that are currently selected. this should work fine, but will clutter a bit if they do a lot of searches and move things between selected/unselected
we dont update songs unless they click update. not rly a problem, only because of previously mentioned issue that when they update the checkboxes clear, so on adding new songs they need to re-check the boxes and update anyway.
"""


@app.route("/", methods=["GET", "POST"])
def load_app():
	return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
	results = []
	query = request.json["query"]  # get search term
	result1 = bs.main(query)
	result2 = bs2.main(query)
	if result1 and not result2:
		results = result1
	elif result2 and not result1:
		results = result2
	elif result1 and result2:
		results = result1 + result2
	search_results = {}
	for i in range(len(results) - 1):
		search_results[str(uuid.uuid4())] = results[i]
	amount = len(search_results)
	return jsonify({"results": search_results, "amount": amount, "keys": list(search_results.keys())})


@app.route("/retrieve_instruments", methods=["POST"])
def retrieve_instruments():
	global all_mid
	all_mid = []
	selected_songs = request.json["selected_songs"]  # get search term
	print(selected_songs)
	files = glob.glob("songs/*")
	for f in files:
		os.remove(f)  # clear songs directory
	failed_songs = []
	keys = selected_songs.keys()
	for key in keys:
		song = selected_songs[key]
		url = song["url"]
		name = song["name"]
		if bs.save_midi(url, name):
			all_mid.append("songs/" + name + ".mid")
		else:
			failed_songs.append(name)
	all_msgs = get_songs_msgs(all_mid)
	instruments = get_instruments(all_msgs)
	return jsonify({"instruments": instruments, "failed_songs": failed_songs})


@app.route("/play", methods=["POST"])
def process():
	data = request.json
	songs = all_mid
	instruments = data["instruments"]
	programs = programs_for_names(instruments)
	savebool = False
	play_song_or_save(songs, savebool, programs)
	# do some tings with it, render with results. play song or give them the file basically
	return jsonify({"success": True})


@app.route("/save", methods=["POST"])
def save():
	data = request.json
	songs = all_mid
	instruments = data["instruments"]
	programs = programs_for_names(instruments)
	savebool = True
	play_song_or_save(songs, savebool, programs)
	return send_file("new_song.mid", as_attachment=True)


def main():
	app.run(debug=True)


if __name__ == "__main__":
	main()
