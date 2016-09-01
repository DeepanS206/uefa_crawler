from Levenshtein import distance
from openpyxl import load_workbook
from matchinfo import matchInfo
from lxml import html
import calendar
import pickle
import shutil
import sys
import os

#returns correct url to start crawler, depending on season, league, and year and group (inx)
def getUrl (season, inx, league):
  url = 'http://www.uefa.com/uefa' + league + '/season=' + season + '/matches/round=' + str(inx) + '/index.html'
  print(url)
  return url

#uses a phantomjs sub-routine to load the jQuery loaded html
#into a file for parsing
def getHtml(url, filename, season):
  filepath = season + '/' + filename
  if not os.path.isdir(season):
    os.mkdir(season)
  cmd = 'phantomjs save_page.js ' + url + ' > ' + filepath
  os.system(cmd)

def delFile(filename):
  os.remove(filename)

def getMonthIndex(calendar, month):
  for i in range(1, 13):
    if (calendar[i] == month):
      if i < 10:
        return "0" + str(i)
      else:
        return str(i)
  return "-1"

def parseDay(day):
  if len(day) == 1:
    return '0' + day
  else:
    return day

def getMatchStats(query_date, season, stage, query_team1, query_team2, filter, league):
  countryDict = {}
  #dictionary consisting of year to the inx in which 
  #the group stage games for that year took place
  seasonDict = {
    "2015":2000587,
    "2014":2000469,
    "2013":2000356,
    "2012":2000272,
    "2011":2000128,
    "2010":2000037,
    "2009":15285,
    "2008":15119
  }

  index = seasonDict[season]

  with open('countryInfo.pickle', 'rb') as handle:
    countryDict = pickle.load(handle)

  #updating inx based off of group
  if stage == 'Finale':
    index = index + 5
  elif stage == 'HF':
    index = index + 4
  elif stage == 'VF':
    index = index + 3
  elif stage == 'AF':
    index = index + 2
  elif stage == 'Zw.':
    index = index + 1
  elif stage == 'Rd':
    index = index - 1

  filepath = season + '/' + stage + '.xml' #filepath to the downloaded html

  if not os.path.exists(filepath):
    file = stage + '.xml'
    url = getUrl(season, index, league)
    getHtml(url, file, season)

  file = season + '/' + stage + '.xml'

  htmlString = ''
  with open(file) as f:
    for line in f:
      htmlString = htmlString + line

  tree = html.fromstring(htmlString) #parsing html into DOM tree with the lxml library
  #table of dates parsed with xpath
  dates = tree.xpath('//div[@class="matchesbyround"]/div[@class="mdsession matchBox innGrid_8 forappnode"]')
  i = 1
  for game_date in dates: #iterating through matches
    datedivs = game_date.xpath('child::div') #getting dates
    for datediv in datedivs: #iterating through dates
      games = datediv.xpath('child::table/tbody') #getting games that happned at that date
      text = datediv.xpath('h3/text()') #getting date
      if not text:
        print('error with dates')
        return
      else:
        text = text[0]
      arr = text.split(' ')
      intMonth = getMonthIndex(calendar.month_name, arr[1])
      day = parseDay(arr[0])
      d = str(intMonth) + '/' + day + '/' + arr[2]
      if (query_date == d): #if date == match date then go through games for that match
        for game in games: #iterate through games in date 
          try:
            matchinfo = game.xpath('tr[@class="sup"]/td[@class="status nob"]')[0].xpath('child::div')[1].xpath('span[@class="report"]/a')
            teaminfo = game.xpath('tr[@class=" match_res"]')[0]
            teams = teaminfo.xpath('child::td')
            team1 = teams[0].xpath('a/text()')[0]
            team2 = teams[4].xpath('a/text()')[0]
            distanceTeam1 = distance(team1, query_team1) #edit-distance algorithm used here since team-names were German
            distanceTeam2 = distance(team2, query_team2) #in the dataset and English in the UEFA website
            filtered = (team1 in filter) | (team2 in filter) #check to see if team names were supposed to be filtered
            constraint = (distanceTeam1 < 3) | (distanceTeam2 < 3) #edit-distance must be less than three to be considered a match
          except:
            print('error occured')
            print("Unexpected error:", sys.exc_info()[0])
            return
          if (constraint) & (not filtered):
            print('match found')
            print(team1 + ' compared to ' + query_team1)
            print(distance(team1, query_team1))
            print(team2 + ' compared to ' + query_team2)
            print(distance(team2, query_team2))
            url = matchinfo[0].xpath('@href')[0] #url to the match statistics page
            info = matchInfo(url, countryDict) #starts crawling the statistics page to get the match information
            info['team1'] = team1
            info['team2'] = team2
            info['filter'] = filter
            return info
    i = i + 1