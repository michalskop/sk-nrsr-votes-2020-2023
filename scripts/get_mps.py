"""Get the list of MPs."""

import datetime
import pandas as pd
import requests_html

# term
term = 9

path = "/home/michal/dev/sk-nrsr-votes-2023-202x/"

data_path = path + "data/"

# load all the votes
votes = pd.read_csv(data_path + "votes.csv")

# get the list of MPs' ids
mp_ids = votes['voter_id'].unique()

# load the mps from the dataset or read them from the web
dont_update_mps = False
if dont_update_mps:
  mps = pd.read_csv(data_path + "mps.csv")
else:
  mps = pd.DataFrame()

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
  in_mp_ids = list(votes.loc[votes['vote_event_id'] == max_vote_event_id]['voter_id'].unique())
  mps['in_parliament'] = mps['mp_id'].isin(in_mp_ids)

# last parliamentary group (from last vote event id for each mp)
# last parliamentary group (from last vote event id for each mp)
last_vote_events = votes.groupby('voter_id')['vote_event_id'].max().reset_index()
last_vote_events.columns = ['voter_id', 'last_vote_event_id']

# if mps already has voter_id and last_vote_event_id columns, replace them with the new ones (correctly by voter_id), otherwise merge them from last_vote_events
if 'voter_id' in mps.columns and 'last_vote_event_id' in mps.columns:
    # Drop existing columns before merging
    mps = mps.drop(columns=['voter_id', 'last_vote_event_id'])
    mps = pd.merge(mps, last_vote_events, left_on='mp_id', right_on='voter_id', how='left')
else:
    # Merge normally if columns don't exist
    mps = pd.merge(mps, last_vote_events, left_on='mp_id', right_on='voter_id', how='left')

mps['last_group_name'] = mps.apply(lambda x: votes.loc[(votes['vote_event_id'] == x['last_vote_event_id']) & (votes['voter_id'] == x['mp_id'])]['group'].iloc[0], axis=1)
mps.to_csv(data_path + "mps.csv", index=False)