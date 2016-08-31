from lxml import html
import pickle
import os

def getNationality(string):
  inx = string.index('(')
  refName = string[:inx-1]
  refNat = string[inx+1:len(string)-1]
  return [refNat, refName]

def extraTime(tree):
  timeline = tree.xpath('//div[@class="grid_12 timeline"]')[0].xpath('child::div')[0].xpath('@class')[0]
  #print(timeline)
  if 'extra' in timeline:
    return True
  return False

def getPenalties (table):
  penaltyHome = 0
  penaltyAway = 0
  for i in range(len(table)):
    tag = table[i].xpath('td[@class="l w155 plev"]')
    if len(tag) == 2:
      innerDiv = tag[0].xpath('div[@class="dinl"]/img')
      if len(innerDiv) != 0:
        for event in innerDiv:
          src = event.xpath('@src')[0]
          boolHome = (src == '/img/icons/event/goals_W.gif') | (src == '/img/icons/event/goals_P.gif')
          if boolHome:
            penaltyHome = penaltyHome + 1
      innerDiv2 = tag[1].xpath('div[@class="dinl"]/img')
      if len(innerDiv2) != 0:
        for event in innerDiv2:
          src = event.xpath('@src')[0]
          boolAway = (src == '/img/icons/event/goals_W.gif') | (src == '/img/icons/event/goals_P.gif')
          if boolAway:
            penaltyAway = penaltyAway + 1
  return str(penaltyHome) + ':' + str(penaltyAway)

def matchInfo (urlext, countryDict):
  dictInfo = {}
  url = 'http://www.uefa.com' + urlext
  cmd = 'phantomjs save_page2.js ' + url + ' > match.xml'
  os.system(cmd)
  htmlString = ''
  with open('match.xml') as f:
    for line in f:
      htmlString = htmlString + line

  tree = html.fromstring(htmlString)
  table = tree.xpath('//table[@class="halfwidth fl"]/tbody/tr')
  dictInfo['penalties'] = getPenalties(table)
  boolean = extraTime(tree)
  dictInfo['extra_time'] = boolean
  #print('Extra Time: ' + str(boolean))

  for i in range(len(table)):
    tag = table[i].xpath('child::td/h2/text()')
    if len(tag) != 0:
      tag2 = tag[0]
      if tag2 == 'Referee':
        inx1 = i + 1
        inx2 = i + 3
        ref = table[inx1].xpath('child::td')[1].xpath('text()')[0]
        assist_refs = table[inx2].xpath('child::td')[1].xpath('text()')[0]
        nationality = getNationality(ref.strip())
        arrAssist = assist_refs.split(',')
        assist1Nat = getNationality(arrAssist[0].strip())
        assist2Nat = getNationality(arrAssist[1].strip())
        dictInfo['ref'] = nationality[1]
        dictInfo['ref_nat'] = countryDict[nationality[0]]
        dictInfo['asstref1'] = assist1Nat[1]
        dictInfo['asstref1_nat'] = countryDict[assist1Nat[0]]
        dictInfo['asstref2'] = assist2Nat[1]
        dictInfo['asstref2_nat'] = countryDict[assist2Nat[0]]

  statgrid = tree.xpath('//div[@class="matchstat"]')[0]
  stattable = statgrid.xpath('child::table/tbody/tr')
  yindex = 0
  rindex = 0
  for i in range(len(stattable)):
   text = stattable[i].xpath('child::td')[0].xpath('text()')[0]
   if text == 'Yellow cards':
    yindex = i
   if text == 'Red Cards':
    rindex = i
  ycards = stattable[yindex].xpath('child::td')
  rcards = stattable[rindex].xpath('child::td')
  ycards_home = ycards[1].xpath('text()')[0]
  ycards_away = ycards[3].xpath('text()')[0]
  rcards_home = rcards[1].xpath('text()')[0]
  rcards_away = rcards[3].xpath('text()')[0]
  dictInfo['yellow_home'] = ycards_home.strip()
  dictInfo['red_home'] = rcards_home.strip()
  dictInfo['red_away'] = rcards_away.strip()
  dictInfo['yellow_away'] = ycards_away.strip()
  os.remove('match.xml')
  return dictInfo