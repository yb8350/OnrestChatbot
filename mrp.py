import re
import math
import datetime
import pandas as pd
from konlpy.tag import Komoran

kom = Komoran(userdic='./UserDictionaryData.txt')
SongLocation = pd.read_csv ('./SongLocation.csv')
EmoDic = pd.read_csv ('./EmotionalDictionary.csv')

negative = [('않', 'VX'), ('못하', 'VX'), ('말', 'VX'), ('아니', 'MAG'), ('아니', 'VCN'), ('안', 'MAG'), ('못', 'MAG'), ('지 않', 'EP'),('지 말', 'EP'),('지 못', 'EP'),('지 마', 'EC'),('지 마라', 'EC'),('진 않', 'EP'),('진 말', 'EP'),('진 못', 'EP'),('진 마', 'EC'),('진 마라', 'EC'),('질 않', 'EP'),('질 못', 'EP'),('질 말', 'EP'),('질 마', 'EC'),('질 마라', 'EC')]
emotion = ['XR', 'VA', 'VV', 'VX', 'NNG', 'MAG', 'NNP', 'MM', 'NA']
angle = [75, 45, 15, 345, 315, 285, 255, 225, 195, 165, 135, 105]

ed = {}
for i in range(len(EmoDic)):
    ed[(EmoDic.abbr[i], EmoDic.wc[i])] = EmoDic.num[i]


#사용자 감정 분석 함수
def emotionAnalysis(diary):
    vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    #1. 영어 제거
    diary = re.sub('[^ㄱ-ㅣ 가-힣 \n]+', '', diary)
    
    #2. 형태소 분석
    try:
        res = kom.pos(diary, flatten=False)
    except:
        return 0, 0
    
    #3. 부정어 처리
    NegSentences = [] 
    d_index = [] 
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
    
    if sum == 0 :
        return 0, 0
    
    for i in range(12):
        vector[i] /= sum
        x += vector[i] * math.cos((angle[i]/180) * math.pi)
        y += vector[i] * math.sin((angle[i]/180) * math.pi)

    x /= 12
    y /= 12
    return x, y


# 좌표를 통해 감정 카테고리 판단하는 함수
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


#감정 분석 결과를 통해 음악 추천 방식을 결정하는 함수
def resultCheck(feelX, feelY, diaryX, diaryY):
    check = -1
    if diaryX == 0 and diaryY == 0:
        if feelX == 0 and feelY == 0:
            return check
        else:
            check = 1
            return check
    elif feelX == 0 and feelY == 0:
        check = 0
        return check
    
    feelCateNum = SelectCategory(feelX, feelY)
    diaryCateNum = SelectCategory(diaryX, diaryY)
    absCateNum = abs(diaryCateNum - feelCateNum)
    
    #1번 카테고리는 2번 카테고리까지만 허용
    if diaryCateNum == 1:
        if absCateNum == 0 or feelCateNum == 2:
            check = 0
    # 카테고리가 같거나 양옆까지만 허용
    elif absCateNum == 0 or absCateNum == 1:
        check = 0
    else:
        check = 1

    return check


#사용자 감정에 가장 근접한 음악 추천 함수
def musicRecommend(diaryX, diaryY):
    leng = len(SongLocation)
    userCategory = SelectCategory(diaryX, diaryY)
    distance = []
    
    for i in range(leng):
        songCategory = SongLocation.CategoryNum[i]
        dis = round(math.sqrt( math.pow(SongLocation.x[i] - diaryX , 2) + math.pow(SongLocation.y[i] - diaryY , 2)), 5)
        distance.append(dis)
        
    SongLocation['distance'] = distance
    resultSort = SongLocation.sort_values(by='distance')
    resultSort = resultSort.reset_index(drop=True)

    result = []
    for i in range(leng):
        songData = []
        if userCategory-1 <= resultSort.CategoryNum[i] and userCategory+1 >= resultSort.CategoryNum[i]:
            songData.append(resultSort.SongName[i])
            songData.append(resultSort.Singer[i])
            songData.append(resultSort.Image[i])
            songData.append(resultSort.SongNum[i])
            result.append(songData)
            
        if len(result) == 3:
            break

    return result


#랜덤 음악 추천 함수
def randomMusic(cateNum):
    bitMask = SongLocation['CategoryNum'] == cateNum
    randomList = SongLocation[bitMask]
    playList = randomList.sample(n=3)

    # result 추천할 곡의 데이터 리스트 형태
    result = []
    for i in range(len(playList)):
        songList = []
        songList.append(playList['SongName'].iloc[i])
        songList.append(playList['Singer'].iloc[i])
        songList.append(playList['Image'].iloc[i])
        songList.append(playList['SongNum'].iloc[i])
        result.append(songList)

    return result