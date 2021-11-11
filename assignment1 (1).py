#import for all tasks
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re
import matplotlib.pyplot as plt
import json
import numpy as np

#find patterns for thr re search
teams = []
with open("rugby.json") as json_file:
    file = json.load(json_file)
for i in file["teams"]:
    teams.append(i["name"])
teamstr = ""
for i in teams:
    teamstr = teamstr + i
    if i != teams[-1]:
        teamstr += "|"
pattern1 = re.compile(teamstr)
pattern2 = r"[0-9]+-[0-9]+"

#create lists to contain data and initial URLs
firstteam = []
scorelist = []
validline = []
main = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/'
base_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/Hodg001.html'
urls = []
heads = []

pagenum = 0

next = []
next.append(base_url)

#go through articles one by one to extract
while next[0] not in urls:
    urls.append(next[0])
    pagenum += 1
    #get texts and links inf
    page = requests.get(next[0])
    soup = BeautifulSoup(page.text, "html.parser")
    links = soup.findAll("a")
    txt = soup.findAll("body")
    txts = txt[0].text

    #find first team
    teamresult = re.findall(pattern1, txts)
    if teamresult:
        firstteam.append(teamresult[0])
    else:
        firstteam.append(None)

    #find scores
    scores = re.findall(pattern2, txts)
    scls = []
    if scores:
        for score in scores:
            a = score.split("-")
            val = int(a[0]) + int(a[1])
            if len(score) < 6 and score != "50-50" and score != "2-1":
                scls.append((val, score))
            scls.sort()
        if scls:
            scorelist.append(scls[-1][-1])
        elif not scls:
            scorelist.append(None)
    elif not scores:
        scorelist.append(None)
    #check of the team name and scores are valid
    if firstteam[pagenum-1] != None and scorelist[pagenum - 1] != None:
        validline.append(pagenum-1)

    headline = soup.findAll("h1")
    heads.append(headline[0].text)

    #empty the next list for next loop
    next = []
    for i in links:
        if (i.string == "Next Article"):
            next.append(urljoin(main, i["href"]))

#creat new lists for valid information
ls1 = []
ls2 = []
ls3 = []
ls4 = []
for num in validline:
    ls1.append(urls[num])
    ls2.append(heads[num])
    ls3.append(firstteam[num])
    ls4.append(scorelist[num])

#task3 average
difflist = []
for item in ls4:
    a = item.split("-")
    val = abs(int(a[0]) - int(a[1]))
    difflist.append(val)

team_dic = {}
i = 0
while i < len(ls3):
    if ls3[i] not in team_dic:
        team_dic[ls3[i]] = [difflist[i]]
    elif ls3[i] in team_dic:
        team_dic[ls3[i]].append(difflist[i])
    i += 1
country = []
averagediff = []
j = 0
while j < len(team_dic):
   country.append(list(team_dic.keys())[j])
   total = 0
   for v in list(team_dic.values())[j]:
       total += v
       average = total / len(list(team_dic.values())[j])
   averagediff.append(average)
   j += 1

#task4 plot
teamfreq = {}
for name in ls3:
    if name not in teamfreq:
        teamfreq[name] = 1
    elif name in teamfreq:
        teamfreq[name] += 1
teamfreq_sorted = sorted(teamfreq.items(), key=lambda item:item[1])
n = -1
xvalue = []
yvalue = []
while n > -6:
    xvalue.append(teamfreq_sorted[n][0])
    yvalue.append(teamfreq_sorted[n][1])
    n -= 1
plt.bar(xvalue, yvalue, 0.5)
plt.xlabel("team name")
plt.ylabel("frequency")
plt.title("team_frequency_chart")
plt.savefig("task4.png")
plt.show()

#task5 plot
freqlist = list(teamfreq.values())
x = np.arange(len(country))
widthlist = []
width = 0.4
w = 0
while w < len(country):
    widthlist.append(width)
    w += 1
plt.bar(x, freqlist, width, align="center", color="b", label="frequence", alpha=1)
plt.bar(x+widthlist, averagediff, width, align="center", color="r", label="avg_game_diff", alpha=1)
plt.xlabel("team name")
plt.xticks(x+width/2, country)
plt.legend()
plt.savefig("task5.png")
plt.show()

#save task1
url_headline = pd.DataFrame({"url": urls, "headline": heads})
url_headline.to_csv("task1.csv", index=False)
#save task2
u_h_t_s = pd.DataFrame({"url": ls1, "headline": ls2, "team": ls3, "score": ls4})
u_h_t_s.to_csv("task2.csv", index=False)
#save task3
diffdata = pd.DataFrame({"team": country, "avg_game_difference": averagediff})
diffdata.to_csv("task3.csv", index=False)
