import bs4
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

	schedules = page_content.find_all('div', attrs={'class' : 'sectioned-day-tables'})[0]

	listOfCourts = schedules.find_all('span', attrs={'class' : 'day-table-heading'})
	#print(listOfCourts)

	for table in schedules.find_all(attrs={'class' : 'day-table'}):
		court = table.find(attrs={'class' : 'day-table-heading'}).contents[0]
		time = table.find(attrs={'colspan' : '10'}).contents[2].strip()
		
		print(court)
		print(table.find(attrs={'colspan' : '10'}).contents[2].strip())

		for match in table.find_all(attrs={'class' : 'day-table-name'}):
			for cont in match.contents:
				if(cont != '\n'):
					if(type(cont) is bs4.element.Tag):
						if(cont.has_attr('data-ga-label')):
							print(cont.attrs['data-ga-label'])
						else:
							for player in cont.find_all('a'):
								print(player.attrs['data-ga-label'])
					else:
						print(cont.strip())
						print(cont.strip())
		print("")



	with open("schedule2.txt", "w") as file:
		for line in page_content.find_all('div', attrs={'class' : 'sectioned-day-tables'}):
			file.write(str(line))


if __name__ == '__main__':
	tourneyList = current_tourneys()
	#print(tourneyList)
	for eachTourney in tourneyList:
		players(eachTourney)