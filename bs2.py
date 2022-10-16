from bs4 import BeautifulSoup
import requests
import json
import time


def scrape_results(search_query):
	html = requests.get(f"https://bitmidi.com/search/?q={search_query}").text
	json_data = get_json(html)
	page_total = json_data["views"]["search"][search_query]["pageTotal"]
	midi_with_names = []
	midi_with_names += get_midi_from_json(json_data)
	for i in range(1, page_total):
		html = requests.get(f"https://bitmidi.com/search/?q={search_query}&page={i}").text
		json_data = get_json(html)
		midi_with_names += get_midi_from_json(json_data)
	return midi_with_names


def get_midi_from_json(json_data):
	all_midis = json_data["data"]["midis"]
	midi_with_names = [{"name": all_midis[key]["name"], "url": "https://bitmidi.com/uploads/" + str(all_midis[key]["id"]) + ".mid"} for key in all_midis]
	return midi_with_names


def get_json(html):
	soup = BeautifulSoup(html, "html.parser")
	data = soup.find_all("script")[1].text.replace("\n", "").split("console.time('render')window.initStore =")[1]
	json_data = json.loads(data)
	return json_data


def save_midi(id, name):
	song = requests.get(f"https://bitmidi.com/uploads/{id}.mid")
	open(f"{name}.mid", "wb").write(song.content)


def main(query):
	results = scrape_results(query)
	return results


if __name__ == '__main__':
	main("")

#     if you want to speed that up it's not that hard just get the number of pages for the search query
#     with json_data["views"]["search"]["mozart"]["pageTotal"] then only run it that number of times
#     where Mozart is your search query

