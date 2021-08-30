import re
import math
import pandas as pd
from konlpy.tag import Komoran

kom = Komoran(userdic='C:/Users/kms/Desktop/crawl/UserDictionaryData.txt')

SongLyrics = pd.read_excel('C:/Users/kms/Desktop/crawl/SongDataCrawl.xlsx')
EmoDic = pd.read_csv('C:/Users/kms/Desktop/crawl/EmotionalDictionary.csv')

#감성사전을 dictionary 형태로 변환
negative = [('않', 'VX'), ('못하', 'VX'), ('말', 'VX'), ('아니', 'VCN'), ('안', 'MAG'), ('못', 'MAG'), ('지 않', 'EP'),('지 말', 'EP'),('지 못', 'EP'),('지 마', 'EC'),('지 마라', 'EC'),('진 않', 'EP'),('진 말', 'EP'),('진 못', 'EP'),('진 마', 'EC'),('진 마라', 'EC'),('질 않', 'EP'),('질 못', 'EP'),('질 말', 'EP'),('질 마', 'EC'),('질 마라', 'EC')]
emotion = ['XR', 'VA', 'VV', 'VX', 'NNG', 'MAG', 'NNP', 'MM', 'NA']
angle = [75, 45, 15, 345, 315, 285, 255, 225, 195, 165, 135, 105]

ed = {}
for i in range(len(EmoDic)):
    ed[(EmoDic.abbr[i], EmoDic.wc[i])] = EmoDic.num[i]
    
# 좌표를 통해 카테고리를 결정하는 함수
def SelectCategory(x, y):
    if x == 0 and y == 0:
        return 0
    myradians = math.atan2(y, x) 
    mydegrees = math.degrees(myradians) 
    if mydegrees >= 60 and mydegrees < 90:
        return 1
    elif mydegrees >= 30 and mydegrees < 60:
        return 2
    elif mydegrees >= 0 and mydegrees < 30:
        return 3
    elif mydegrees >= -30 and mydegrees < 0:
        return 4
    elif mydegrees >= -60 and mydegrees < -30:
        return 5
    elif mydegrees >= -90 and mydegrees < -60:
        return 6
    elif mydegrees >= -120 and mydegrees < -90:
        return 7
    elif mydegrees >= -150 and mydegrees < -120:
        return 8
    elif mydegrees >= -180 and mydegrees < -150:
        return 9
    elif mydegrees >= 150 and mydegrees < 180:
        return 10
    elif mydegrees >= 120 and mydegrees < 150:
        return 11
    elif mydegrees >= 90 and mydegrees < 120:
        return 12

#가사의 감정값을 분석하는 함수
def LyricsEmotion(ly) :  
    vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    #1. 영어 제거
    ly = re.sub('[^ㄱ-ㅣ 가-힣 \n]+', '', ly)
    ly = re.sub('\n{2,}', '\n', ly)
    ly = re.sub('[ ]*\n[ ]+', '', ly)
    ly = ly.strip()
    
    #2. 형태소 분석기 돌리기
    try:
        res = kom.pos(ly, flatten=False)
    except:
        return 0, 0
    
    #3. 부정어 처리
    NegSentences = [] #부정어가 포함된 문장
    d_index = [] #부정어가 포함된 문장의 인덱스
    for i in range(len(res)):
        for j in range(len(res[i])):
            if res[i][j] in negative :
                NegSentences.append(res[i])
                d_index.append(i)
                break
    d_index.reverse()
    if len(d_index) > 0:
        for i in d_index:
            del res[i]
    
    emo = []
    neg = False
    for ng in NegSentences :
        for i in range(len(ng)):
            if ng[i] in negative:
                neg = True
            if ng[i][1] == 'EC' or ng[i][1] == 'EF':
                if len(emo) > 0 and neg == True :
                    for i in emo:
                        if i < 6 :
                            vector[i+6] += 1;
                        else:
                            vector[i-6] += 1;
                else:
                    if len(emo) > 0:
                        for i in emo:
                            vector[i] += 1;
                            
                emo = []
                neg = False
            elif ng[i] in ed.keys():
                emo.append(ed[ng[i]]-1)
            
    
    #4. 필요없는 품사 제거 + BoW
    word = {}
    bow = []
    for voca in res:
        for i in range(len(voca)):
            if voca[i][1] in emotion:
                if voca[i] not in word.keys():
                    word[voca[i]] = len(word)
                    bow.insert(len(word)-1,1)
                else:
                    index = word.get(voca[i])
                    bow[index] += 1
    
    #5. 감성사전 탐색
    for w in word:
        if w in ed.keys():
            vector[ed[w]-1] += bow[word.get(w)]
      
    #6. 정규화, 좌표값 계산
    sum = 0
    x = 0
    y = 0
    for i in vector:
        sum += i
    
    if sum <= 5:
        return 0, 0
    
    for i in range(12):
        vector[i] /= sum
        x += vector[i] * math.cos((angle[i]/180) * math.pi)
        y += vector[i] * math.sin((angle[i]/180) * math.pi)
    
    x = round(x / 12, 10)
    y = round(y / 12, 10)

    return x, y

data = []
for i in range(len(SongLyrics)) :
    x, y = LyricsEmotion(SongLyrics.Lyrics[i])
    n = SelectCategory(x, y)
    data.append([SongLyrics.Singer[i], SongLyrics.SongName[i], SongLyrics.Image[i], SongLyrics.SongNum[i], x, y, n])
    
df = pd.DataFrame(data, columns = ['Singer', 'SongName', 'Image','SongNum', 'x', 'y', 'CategoryNum'])
df.to_csv("C:/Users/kms/Desktop/crawl/SongLocation.csv", index=False)