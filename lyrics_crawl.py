import re
import time
import requests
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

driver = webdriver.Chrome("C:/Users/kms/Desktop/crawl/chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("disable-gpu") # 가속 사용 x
options.add_argument("lang=ko_KR") # 임시 플러그인 탑재
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36") #user-agent 이름
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}

ad = pd.read_excel('C:/Users/kms/Desktop/crawl/SongList.xlsx')
data = []

for i in range(len(ad)):
    url = 'https://www.genie.co.kr/search/searchMain?query=' + str(ad.Singer[i]) + " " + str(ad.SongName[i]) #곡 검색
    driver.get(url) #cromedriver를 이용해 url 실행
    time.sleep(2)
    try:
        driver.find_element_by_class_name('btn-basic.btn-info').click() #첫 번째 곡 세부 정보 클릭
    except:
        print(ad.Singer[i], " ", ad.SongName[i])
        continue
    html = requests.get(driver.current_url, headers = headers).text
    soup = BeautifulSoup(html, 'html.parser') #BeautifulSoup를 이용해 html 실행
    Singer = soup.select('ul.info-data > li > span.value')[0].get_text()
    SongName = re.sub(' [-].+', '', soup.select('pre#pLyrics > div')[0].get_text())
    Lyrics = soup.select('div.tit-box > pre > p')[0].get_text()
    Genre = soup.select('ul.info-data .value')[2].get_text()
    SongNum = soup.select('#add_my_album_top')[0]['songid']
    Image = soup.select('span.cover img')[0]['src']
    
    data.append([Singer, SongName, Lyrics, Genre, SongNum, Image]) #리스트에 데이터 저장
    a = random.randrange(1,5)
    time.sleep(a)
    if i % 10 == 0:
        print(i)
    if i % 100 == 0 and i != 0:
        time.sleep(30)

df = pd.DataFrame(data, columns = ['Singer', 'SongName', 'Lyrics', 'Genre', 'SongNum', 'Image'])
df.to_excel("C:/Users/kms/Desktop/crawl/SongDataCrawl.xlsx", index=False)