import bs4
from bs4 import BeautifulSoup
import requests
import boto3
from boto3.dynamodb.conditions import Key, Attr
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

def eventDayChanged(tournament):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table("Tournament")

	page_link = atp + tournament
	page_response = requests.get(page_link, timeout=5)
	page_content = BeautifulSoup(page_response.content, "html.parser")

	tourney = page_content.find('a', attrs={'class' : 'tourney-title'}).contents[0].strip()
	day = page_content.find('span', attrs={'class' : 'day-table-day'}).contents[0].strip()
	day = ' '.join(day.split())

	#print(tourney)
	#print(day)

	response = table.get_item(
		Key={
			'Tourney' : tourney
		}
	)
	if('Item' in response.keys()):
		if(response['Item']['Day'] == day):
			return False
		else:
			table.put_item(
				Item={
				'Tourney' : tourney,
				'Day' : day
				}
			)
	else:
		table.put_item(
			Item={
			'Tourney' : tourney,
			'Day' : day
			}
		)
	
	return True

def players(tournament):
	page_link = atp + tournament
	page_response = requests.get(page_link, timeout=5)
	page_content = BeautifulSoup(page_response.content, "html.parser")

	schedules = page_content.find_all('div', attrs={'class' : 'sectioned-day-tables'})[0]
	tourney = page_content.find('a', attrs={'class' : 'tourney-title'}).contents[0].strip()
	tourney_location = page_content.find('span', attrs={'class' : 'tourney-location'}).contents[0].strip()
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
							setDict(info, cont.attrs['data-ga-label'], court, time, day, orderOfPlay, tourney, tourney_location)
						else:
							twoPlayers = False
							if(len(cont.find_all('a')) > 1):
								twoPlayers = True
							for player in cont.find_all('a'):
								#print(player.attrs['data-ga-label'])
								setDict(info, player.attrs['data-ga-label'], court, time, day, orderOfPlay, tourney, tourney_location)
								if(twoPlayers):
									allInfo.append(info)
									twoPlayers = False
					else:
						setDict(info, cont.strip(), court, time, day, orderOfPlay, tourney, tourney_location)
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

def setDict(info, player, court, time, day, order, tourney, tourney_location):
	info["Player"] = player
	info["Court"] = court
	info["Time"] = time
	info["Day"] = day
	info["Order"] = order
	info["Tourney"] = tourney
	info["Tourney_Location"] = tourney_location


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
				'Day' : player["Day"],
				'Order' : player["Order"],
				'Tourney' : player["Tourney"],
				'Tourney_Location' : player["Tourney_Location"]
			}
		)

def deleteDB():
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table("TennisTimes")

	response = table.scan()

	with table.batch_writer() as batch:
		for each in response['Items']:
			batch.delete_item(
				Key={
					'Player' : each['Player']
				})


if __name__ == '__main__':
	#deleteDB()
	tourneyList = current_tourneys()
	for eachTourney in tourneyList:
		if(eventDayChanged(eachTourney)):
			print("Updating DB for new dates")
			deleteDB()
			playersList = players(eachTourney)
			updateDB(playersList)
		else:
			print("No changes")
	#pprint.pprint(playersList)