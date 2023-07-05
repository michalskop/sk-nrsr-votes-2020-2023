"""Several statistics for MPs - different approach, counts only."""

import pandas as pd
import requests_html

# term
term = 8

data_path = "data/"

# get the list of MPs
mps = pd.read_csv(data_path + "mps.csv")

# load attendance
attendance = pd.read_csv(data_path + "attendance.v1.all.csv")

# merge attendance to mps
mps = pd.merge(mps, attendance.loc[:, ['mp_id', 'name', 'photo_url', 'attendance', 'possible']], on='mp_id', how='left')

max_possible = mps['possible'].max()

# create a session
session = requests_html.HTMLSession()


# test
mp_id = 858 # Kuffa
mp_id = 808 # Matovič
mp_id = 997 # Blcháč
mp_id = 1003 # Čepček
mp_id = 1078 # Kuriak
mp_id = 779 # Dostál

# statistics
statistics = {
  # ho = hodina otázok = question hour
  # 'ho': {
  #   'url': 'https://www.nrsr.sk/web/Default.aspx?sid=schodze/ho_result&AssignerId={}&CisObdobia={}',
  #   'n': 50, # per page
  #   'target': '_sectionLayoutContainer$ctl01$_ResultGrid'
  # },
  # # interpellations
  # 'interpellations': {
  #   'url': 'https://www.nrsr.sk/web/Default.aspx?sid=schodze/interpelacie_result&ZadavatelId={}&CisObdobia={}',
  #   'n': 50, # per page
  #   'target': '_sectionLayoutContainer$ctl01$_ResultGrid'
  # },
  # 'amendments': {
  #   'url': 'https://www.nrsr.sk/web/Default.aspx?sid=schodze/nrepdn&PoslanecMasterID={}&CisObdobia={}',
  #   'n': 50, # per page
  #   'target': '_sectionLayoutContainer$ctl01$dgResult'
  # },
  # # legislative initiative = návrhy zákonov
  'legislative_initiative': {
    'url': 'https://www.nrsr.sk/web/Default.aspx?sid=zakony/sslp&PredkladatelID=0&PredkladatelPoslanecId={}&CisObdobia={}',
    'n': 10, # per page
    'target': '_sectionLayoutContainer$ctl01$_ResultGrid'
  }
  # amendments = pozmeňujúce návrhy,
  # 'speeches': {
  #   'url': 'https://www.nrsr.sk/web/Default.aspx?sid=schodze/rozprava/vyhladavanie&CPT=&CisSchodze=0&PoslanecID={}&DatumOd=1900-1-1%200:0:0&DatumDo=2100-1-1%200:0:0&TypVystupenia=&CisObdobia={}',
  #   'n': 20, # per page
  #   'target': '_sectionLayoutContainer$ctl01$_ResultGrid'
  # }
}

for stat in statistics:
  mps[stat] = 0

# for all statistics:
for stat in statistics:
  # for all MPs
  ii = 0
  for mp_id in mps['mp_id']:
    url = statistics[stat]['url']
    print(ii, url.format(mp_id, term))
    r = session.get(url.format(mp_id, term))
    hidden_inputs = r.html.find("input[type='hidden']")
    form_values = {input_elem.attrs['name']: input_elem.attrs.get('value', '') for input_elem in hidden_inputs}
    hoz = 0

    # test for existence of questions
    if r.html.text.find("ie sú evidované") > 0:
      last_page = 1
    else:
      # ho += len(r.html.find(".tab_zoznam", first=True).find("[target='_self']"))
      hoz += len(r.html.find(".tab_zoznam", first=True).find(".tab_zoznam_nonalt"))
      hoz += len(r.html.find(".tab_zoznam", first=True).find(".tab_zoznam_alt"))
      hoz += len(r.html.find(".tab_zoznam", first=True).find(".tab_zoznam_nalt"))
      try:
        lpl = r.html.find(".pager", first=True).find("tr", first=True).text.split("\n")
        last_sign = lpl[len(lpl) - 1]
        # if it is more than 10, it displays '»'
        # we download last page and get the number of pages
        if last_sign == '»':
          datax = form_values.copy()
          datax['__EVENTARGUMENT'] = "Page$Last"
          datax['__EVENTTARGET'] = statistics[stat]['target']
          r1 = session.post(url.format(mp_id, term), data=datax)
          lpl1 = r1.html.find(".pager", first=True).find("tr", first=True).text.split("\n")
          last_page = int(lpl1[len(lpl1) - 1])
        else:
          last_page = int(lpl[len(lpl) - 1])
      except: 
        last_page = 1

    # get last page
    if last_page > 1:
      datax = form_values.copy()
      datax['__EVENTARGUMENT'] = "Page$" + str(last_page) # or "Page$Last"
      datax['__EVENTTARGET'] = statistics[stat]['target']
      print(url.format(mp_id, term), "page=" + str(last_page))
      r1 = session.post(url.format(mp_id, term), data=datax)
      hoz = 0
      try:
        hoz += len(r1.html.find(".tab_zoznam", first=True).find(".tab_zoznam_nonalt"))
        hoz += len(r1.html.find(".tab_zoznam", first=True).find(".tab_zoznam_alt"))
        hoz += len(r1.html.find(".tab_zoznam", first=True).find(".tab_zoznam_nalt"))
      except:
        hoz = 0

    # insert ho into mps
    if last_page > 1:
      mps.loc[mps['mp_id'] == mp_id, stat] = (last_page - 1) * statistics[stat]['n'] + hoz
    else:
      mps.loc[mps['mp_id'] == mp_id, stat] = hoz
    
    ii += 1
    

mps.to_csv(data_path + "mps.stat.test2.csv", index=False)

