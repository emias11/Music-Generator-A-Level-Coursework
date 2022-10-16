import requests
from bs4 import BeautifulSoup
mydict = {}
html = requests.get("https://www.midi.org/specifications-old/item/gm-level-1-sound-set").text
soup = BeautifulSoup(html, "html.parser")
instruments = soup.find_all("table")[1].find_all("tr")[3:]
for instrument in instruments:
	tds = instrument.find_all("td")
	mydict[int(tds[0].text.replace(".", ""))] = tds[1].text
print(mydict)