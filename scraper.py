import bs4
from bs4 import BeautifulSoup
import requests
import boto3
import pprint

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

	day = str(page_content.find('h3', attrs={'class' : 'day-table-date'}).contents[0])

	allInfo = []

	for table in schedules.find_all(attrs={'class' : 'day-table'}):

		court = str(table.find(attrs={'class' : 'day-table-heading'}).contents[0])
		time = table.find(attrs={'colspan' : '10'}).contents[2].strip()
		orderOfPlay = 1		

		#print(court)
		#print(table.find(attrs={'colspan' : '10'}).contents[2].strip())

		for match in table.find_all(attrs={'class' : 'day-table-name'}):
			#print(match.contents)
			for cont in match.contents:
				if(cont != '\n'):
					info = {}
					if(type(cont) is bs4.element.Tag):
						if(cont.has_attr('data-ga-label')):
							#print(cont.attrs['data-ga-label'])
							setDict(info, cont.attrs['data-ga-label'], court, time, day, orderOfPlay)
						else:
							twoPlayers = False
							if(len(cont.find_all('a')) > 1):
								twoPlayers = True
							for player in cont.find_all('a'):
								#print(player.attrs['data-ga-label'])
								setDict(info, player.attrs['data-ga-label'], court, time, day, orderOfPlay)
								if(twoPlayers):
									allInfo.append(info)
									twoPlayers = False
					else:
						setDict(info, cont.strip(), court, time, day, orderOfPlay)
						orderOfPlay += 1
						#print(cont.strip())
					allInfo.append(info)
			orderOfPlay += 1
		
		#print("")
		#break
	#print(allInfo)
	return allInfo


	#with open("schedule2.txt", "w") as file:
	#	for line in page_content.find_all('div', attrs={'class' : 'sectioned-day-tables'}):
	#		file.write(str(line))

def setDict(info, player, court, time, day, order):
	info["Player"] = player
	info["Court"] = court
	info["Time"] = time
	info["Day"] = day
	info["Order"] = order


def updateDB(playersList):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table("TennisTimes")

	for player in playersList:
		player_name = player["Player"]
		court = str(player["Court"])
		time = player["Time"]
		table.put_item(
			Item={
				'Player' : player_name,
				'Court' : str(player["Court"]),
				'Time' : player["Time"],
				'Order' : player["Order"]
			}
		)


if __name__ == '__main__':
	deleteDB()
	tourneyList = current_tourneys()
	#print(tourneyList)
	for eachTourney in tourneyList:
		playersList = players(eachTourney)
		#updateDB(playersList)
	#pprint.pprint(playersList)