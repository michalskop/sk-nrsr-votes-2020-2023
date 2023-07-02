"""Get the list of MPs."""

import datetime
import pandas as pd
import requests_html

# term
term = 8

data_path = "data/"

# load all the votes
votes = pd.read_csv(data_path + "votes.csv")

# get the list of MPs' ids
mp_ids = votes['mp_id'].unique()

# create a session
session = requests_html.HTMLSession()

# get the MPs' info
mps = pd.DataFrame()

url = "https://www.nrsr.sk/web/Default.aspx?sid=poslanci/poslanec&PoslanecID={}&CisObdobia={}"

for mp_id in mp_ids:
  print(mp_id)
  r = session.get(url.format(mp_id, term))
  try:
    birthday = datetime.datetime.strptime(r.html.find(".mp_personal_data", first=True).find("div")[5].find("span", first=True).find("span", first=True).text, '%d. %m. %Y').date().isoformat()
  except:
    birthday = None
  mp = {
    "mp_id": mp_id,
    "given_name": r.html.find(".mp_personal_data", first=True).find("div", first=True).find("span", first=True).text,
    "family_name": r.html.find(".mp_personal_data", first=True).find("div")[3].find("span", first=True).find("span", first=True).text,
    "title": r.html.find(".mp_personal_data", first=True).find("div")[2].find("span", first=True).find("span", first=True).text,
    "list": r.html.find(".mp_personal_data", first=True).find("div")[4].find("span", first=True).find("span", first=True).text,
    "born_on": birthday,
    "nationality": r.html.find(".mp_personal_data", first=True).find("div")[6].find("span", first=True).find("span", first=True).text,
    "municipality": r.html.find(".mp_personal_data", first=True).find("div")[7].find("span", first=True).find("span", first=True).text,
    "region": r.html.find(".mp_personal_data", first=True).find("div")[8].find("span", first=True).find("span", first=True).text,
    "email": r.html.find(".mp_personal_data", first=True).find("div")[9].find("span", first=True).find("span", first=True).text
  }
  mps = pd.concat([mps, pd.DataFrame([mp])])

# in_parliament
max_vote_event_id = votes['vote_event_id'].max()
in_mp_ids = list(votes.loc[votes['vote_event_id'] == max_vote_event_id]['mp_id'].unique())
mps['in_parliament'] = mps['mp_id'].isin(in_mp_ids)

mps.to_csv(data_path + "mps.csv", index=False)