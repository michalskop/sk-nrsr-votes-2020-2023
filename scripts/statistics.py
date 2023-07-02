"""Prepare different statistics for MPs."""

import pandas as pd

data_path = "data/"

# attendance
votes = pd.read_csv(data_path + "votes.csv")
mps = pd.read_csv(data_path + "mps.csv")

attendance = pd.pivot_table(votes, index='voter_id', columns='option', values='vote_event_id', aggfunc='count', fill_value=0)

attendance['attendance'] = attendance['yes'] + attendance['no'] + attendance['abstain']
attendance['possible'] = attendance['attendance'] + attendance['not voting'] + attendance['absent']
attendance['rate'] = attendance['attendance'] / attendance['possible']

# merge with mps
attendance = pd.merge(attendance, mps, left_on='voter_id', right_on='mp_id')

# only current mps
attendance = attendance[attendance['in_parliament']]

# photo url, name
attendance['photo_url'] = attendance.apply(lambda x: "https://www.nrsr.sk/web/dynamic/PoslanecPhoto.aspx?PoslanecID=" + str(x['mp_id']) + "&ImageWidth=140", axis=1)
attendance['name'] = attendance['given_name'] + " " + attendance['family_name']

# output v.1
output = attendance[['mp_id', 'given_name', 'family_name', 'name', 'photo_url', 'list', 'attendance', 'possible', 'rate']]
output['účasť'] = (output['rate'] * 100).round(0).astype(int)
del output['rate']

# change OĽANO
output['list'] = output['list'].replace('OBYČAJNÍ ĽUDIA a nezávislé osobnosti (OĽANO), NOVA, Kresťanská únia (KÚ), ZMENA ZDOLA', 'OĽANO, NOVA, KÚ, ZMENA ZDOLA')

output.sort_values(by=['list'], inplace=True)

output.to_csv(data_path + "attendance.v1.csv", index=False)
