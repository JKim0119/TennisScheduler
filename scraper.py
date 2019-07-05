from bs4 import BeautifulSoup
import requests

atp = "https://www.atptour.com"

def current_tourneys():
	curr = []

	page_link = atp + "/en/tournaments"
	page_response = requests.get(page_link, timeout=5)
	page_content = BeautifulSoup(page_response.content, "html.parser")

	for line in page_content.find_all('a', href=True, attrs={'data-ga-label' : "Schedule"}):
		curr.append(line.attrs['href'])

	return curr

def players(tourney):
	page_link = atp + tourney
	page_response = requests.get(page_link, timeout=5)
	page_content = BeautifulSoup(page_response.content, "html.parser")
	
	with open("schedule.txt", "w") as file:
		file.write(str(page_content))


if __name__ == '__main__':
	tourneyList = current_tourneys()
	print(tourneyList)
	for eachTourney in tourneyList:
		players(eachTourney)