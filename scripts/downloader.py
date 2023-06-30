"""Downloads the votes."""

import datetime
import pandas as pd
# import requests
import re
import requests_html

# create a session
session = requests_html.HTMLSession()

# vote_events_minmax = [43678, 50570] # original
vote_events_minmax = [50571, 50825]
nrsr_org_id = 13

url = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/hlasovanie/hlasklub&ID={}"

# votes = pd.DataFrame()
# vote_events = pd.DataFrame()
votes = pd.read_csv("data/votes.csv")
vote_events = pd.read_csv("data/vote_events.csv")

option2option = {
  'Z': 'yes',
  'P': 'no',
  '?': 'abstain',
  'N': 'not voting',
  '0': 'absent',
  '-': 'not member'
}

# vote_event_id = 50570
for vote_event_id in range(vote_events_minmax[0], vote_events_minmax[1] + 1):
  # print vote_event_id
  if vote_event_id % 10 == 0:
    print(vote_event_id)
    vote_events.to_csv("data/vote_events.csv", index=False)
    votes.to_csv("data/votes.csv", index=False)
  
  # get url
  r = session.get(url.format(vote_event_id))

  # vote event info
  vote_event = {
    "vote_event_id": vote_event_id,
    "org_id": nrsr_org_id
  }
  # sitting
  try:
    vote_event['sitting'] = re.findall(r'\d+', r.html.find("#_sectionLayoutContainer_ctl01_ctl00__schodzaLink", first=True).text.split("\n")[0])[0]
    # table
    table = r.html.find(".voting_stats_summary_full", first=True)
    # date and time
    dt = table.find(".grid_4")[1].find("span", first=True).text
    datetime_obj = datetime.datetime.strptime(dt, '%d. %m. %Y %H:%M')
    vote_event['date'] = datetime_obj.date().isoformat()
    vote_event['time'] = datetime_obj.time().isoformat()
    # vote event number
    vote_event['vote_event_number'] = table.find(".grid_4")[2].find("span", first=True).text
    # name
    vote_event['name'] = table.find(".grid_12", first=True).find("span", first=True).text
    # result
    res = table.find("#_sectionLayoutContainer_ctl01_ctl00__votingResultCell", first=True).find("span", first=True).text
    if res == "Návrh prešiel":
      vote_event['result'] = "pass"
    else:
      vote_event['result'] = "fail"
    # numbers
    try:
      numbers = table.find("#_sectionLayoutContainer_ctl01_ctl00__resultsTablePanel", first=True)
      vote_event['present'] = numbers.find("span")[0].text
      vote_event['voted'] = numbers.find("span")[1].text
      vote_event['yes'] = numbers.find("span")[2].text
      vote_event['no'] = numbers.find("span")[3].text
      vote_event['abstain'] = numbers.find("span")[4].text
      vote_event['not voting'] = numbers.find("span")[5].text
      vote_event['absent'] = numbers.find("span")[6].text
    except:
      pass
    # append
    vote_events = pd.concat([vote_events, pd.DataFrame(vote_event, index=[0])], ignore_index=True)
    
    # votes
    try:
      vtable = r.html.find("#_sectionLayoutContainer_ctl01__resultsTable", first=True)
      group_name = ""
      i = 0
      for row in vtable.find("td"):
        try:
          cl = row.attrs['class']
          group_name = row.text
        except:
          try:
            mp_name = row.find("a", first=True).text
            mp_id = re.findall(r'ID=(\d+)', row.find("a", first=True).attrs['href'])[0]
            option_raw = re.findall(r'\[(.*)\]', row.text)[0]
            option = option2option[option_raw]
            vote = {
              "vote_event_id": vote_event_id,
              "mp_id": mp_id,
              "option": option,
              "group": group_name
            }
            votes = pd.concat([votes, pd.DataFrame(vote, index=[0])], ignore_index=True)
          except:
            pass
        i += 1
    except:
      pass
  except:
    pass

  # break

# remove duplicates
votes = votes.drop_duplicates(['vote_event_id', 'mp_id'])
vote_events = vote_events.drop_duplicates(['vote_event_id'])

vote_events.to_csv("data/vote_events.csv", index=False)
votes.to_csv("data/votes.csv", index=False)
