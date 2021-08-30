import mrp
import requests
import base64
import pymysql
import datetime
import pandas as pd
from flask import Flask, request, jsonify

application = Flask(__name__)

#일기 DB 저장 함수
def chatDB(result):
    conn = pymysql.connect(host = "musicchat.cik9oz7kscya.ap-northeast-2.rds.amazonaws.com",
                           user="jeong",
                           passwd="thwjd71410!",
                           db="musicChat",
                           port=3306,
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    req = request.get_json()
    songNum1 = result[0][3]
    songNum2 = result[1][3]
    songNum3 = result[2][3]
    userid = req["userRequest"]["user"]["id"]
    mainEmo = req["action"]["params"]["feel"]
    diary = req["action"]["params"]["diary"]
    nowDate = req["action"]["detailParams"]["date"]["origin"]
    query = """INSERT INTO musicChat.musicChat (userid, nowdate, mainEmo, diary, songNum1, songNum2, songNum3) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    val = (userid, nowDate, mainEmo, diary, songNum1, songNum2, songNum3)
    cursor.execute(query, val)

    conn.commit()
    conn.close()
    

@application.route('/diarymusic', methods=['POST'])
def diarymusic():
    req = request.get_json()
    feelX, feelY = mrp.emotionAnalysis(req["action"]["params"]["feel"])
    diaryX, diaryY = mrp.emotionAnalysis(req["action"]["params"]["diary"])
    check = mrp.resultCheck(feelX, feelY, diaryX, diaryY)
    print(check)
    resultText = "당신의 오늘에 어울릴 노래를 뽑아봤어요."
    if check == 0:
        result = mrp.musicRecommend(diaryX, diaryY)
    elif check == 1:
        result = mrp.randomMusic(mrp.SelectCategory(feelX, feelY))
    else:
        result = mrp.randomMusic(0)
        resultText = "일기의 감정을 잘 이해하지 못했어요. \n어느날에나 듣기 좋은 노래를 추천드릴게요!"

    chatDB(result)
    
    
    res =  {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "simpleText": {
              "text": resultText
            }
          },
          {
            "listCard": {
              "header": {
                "title": "곡 추천 결과"
              },
              "items": [
                {
                  "title": result[0][0],
                  "description": result[0][1],
                  "imageUrl": "https:" + str(result[0][2]),
                  "link": {
                    "web": "http://mw.genie.co.kr/detail/songInfo?xgnm="+str(result[0][3])
                  }
                },
                {
                  "title": result[1][0],
                  "description": result[1][1],
                  "imageUrl": "https:" + str(result[1][2]),
                  "link": {
                    "web": "http://mw.genie.co.kr/detail/songInfo?xgnm="+str(result[1][3])
                  }
                },
                {
                  "title": result[2][0],
                  "description": result[2][1],
                  "imageUrl": "https:" + str(result[2][2]),
                  "link": {
                    "web": "http://mw.genie.co.kr/detail/songInfo?xgnm="+str(result[2][3])
                  }
                }
              ]
            }
          },
          {
            "basicCard": {
              "title": "오늘 추천받은 노래 중 가장 마음에 드는 노래를 골라주세요",
              "buttons": [
                {
                  "action": "block",
                  "label": "첫 번째 곡",
                  "blockId": "6118b3ecee2e484fe68aec89",
                  "messageText": result[0][0] + " - " + result[0][1],
                  "extra" : {
                    "message": int(result[0][3])
                  }
                },
                {
                   "action": "block",
                   "label": "두 번째 곡",
                   "blockId": "6118b3ecee2e484fe68aec89",
                   "messageText": result[1][0] + " - " + result[1][1],
                   "extra" : {
                     "message": int(result[1][3])
                   }
                },
                {
                   "action": "block",
                   "label": "세 번째 곡",
                   "blockId": "6118b3ecee2e484fe68aec89",
                   "messageText": result[2][0] + " - " + result[2][1],
                   "extra" : {
                     "message": int(result[2][3])
                   }
                }
              ]
            }
          }
        ]
      }
    }
    return jsonify(res)


@application.route('/feedback', methods=['POST'])
def feedback():
    conn = pymysql.connect(host = "musicchat.cik9oz7kscya.ap-northeast-2.rds.amazonaws.com",
                           user="jeong",
                           passwd="thwjd71410!",
                           db="musicChat",
                           port=3306,
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    req = request.get_json()
    satisSong = req["action"]["clientExtra"]
    key = satisSong['message']
    feedback = req["action"]["detailParams"]["feedback"]["value"]
    agreement = req["action"]["detailParams"]["open"]["value"]
    userid = req["userRequest"]["user"]["id"]
    nowDate = req["action"]["detailParams"]["date"]["origin"]
    resultText = "온쉼표의 발전을 위해 사용자들에게 피드백을 받고 있습니다. 피드백을 제공해주시겠어요?"
    
    if feedback == "yes":
        feedNum = 1
    else:
        feedNum = 0
        
    if agreement == "yes":
        agreeNum = 1
    else: 
        resultText = "소중한 데이터를 제공해주셔서 감사합니다! 온쉼표의 발전을 위해 사용자들에게 피드백을 받고 있습니다. 피드백을 제공해주시겠어요?"
        agreeNum = 0
        
    query = """UPDATE musicChat.musicChat SET feedback = %s, agreement = %s, satisSong = "%s" WHERE userid = %s AND nowdate = %s;"""
    val = (feedNum, agreeNum, key, userid, nowDate)
    cursor.execute(query, val)
    conn.commit()
    conn.close()
    res = {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "simpleText": {
              "text": resultText
            }
          }
        ],"quickReplies": [
            {
                "action": "block",
                "label": "네",
                "blockId": "611a9193a5a4854bcb950974"
            },
            {
                "action": "block",
                "label": "아니오",
                "blockId": "611a919aee2e484fe68aef3f"
          }
        ]
      }
    }
    
    return jsonify(res)


@application.route('/feelmusic', methods=['POST'])
def feelmusic():

    req = request.get_json()
    mainX, mainY = mrp.emotionAnalysis(req["action"]["params"]["feel"])
   
    result = mrp.randomMusic(mrp.SelectCategory(mainX, mainY))

    res = {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "simpleText": {
              "text": "당신의 오늘에 어울릴 노래를 뽑아봤어요."
            }
          },
          {
            "listCard": {
              "header": {
                "title": "곡 추천 결과"
              },
              "items": [
                {
                  "title": result[0][0],
                  "description": result[0][1],
                  "imageUrl": "https:" + str(result[0][2]),
                  "link": {
                    "web": "http://mw.genie.co.kr/detail/songInfo?xgnm="+str(result[0][3])
                  }
                },
                {
                  "title": result[1][0],
                  "description": result[1][1],
                  "imageUrl": "https:" + str(result[1][2]),
                  "link": {
                    "web": "http://mw.genie.co.kr/detail/songInfo?xgnm="+str(result[1][3])
                  }
                },
                {
                  "title": result[2][0],
                  "description": result[2][1],
                  "imageUrl": "https:" + str(result[2][2]),
                  "link": {
                    "web": "http://mw.genie.co.kr/detail/songInfo?xgnm="+str(result[2][3])
                  }
                }
              ]
            }
          }
        ],
        "quickReplies": [
          {
            "action": "block",
            "label": "처음으로",
            "blockId": "61181c9725cb590ace33e6fd"
          }
        ]
      }
    }

    return jsonify(res)


@application.route('/diarysearch1', methods=['POST'])
def dairysearch1():
    conn = pymysql.connect(host = "musicchat.cik9oz7kscya.ap-northeast-2.rds.amazonaws.com",
                           user="jeong",
                           passwd="thwjd71410!",
                           db="musicChat",
                           port=3306,
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)

    cursor = conn.cursor()
    req = request.get_json()
    userid = req["userRequest"]["user"]["id"]
    diaryDate = req["action"]["detailParams"]["diaryDate"]["origin"]
    userDate = datetime.datetime.strptime(diaryDate, "%Y-%m")
    lastMonth = userDate.month
    lastYear = userDate.year
    
        
    query = """SELECT * FROM musicChat.musicChat WHERE userid=%s AND MONTH(nowdate)=%s AND YEAR(nowdate) = %s order by nowdate;"""
    val = (userid, lastMonth, lastYear)
    cursor.execute(query, val)
    dataCur = cursor.fetchall()
    textResult = "%s년 %s월에 일기를 작성한 날짜에요." % (lastYear, lastMonth) + '\n' + "일기 내용을 조회하시려면 일기 상세 조회를 눌러주세요." + '\n' +  "----------------------------------" + '\n' + " [작성 날짜]    [기분]" + '\n'
    
    conn.close()

    for i in dataCur:
        textResult = textResult + i["nowdate"] + "  " + i["mainEmo"] + '\n'

    if not dataCur:
        textResult = "선택하신 달에 조회할 일기가 없습니다."

        res = {
          "version": "2.0",
         "template": {
              "outputs": [
                      {
                    "simpleText": {
                        "text": textResult
                    
            }
          }  
        ],"quickReplies": [
            {
                "action": "block",
                "label": "처음으로",
                "blockId": "61181c9725cb590ace33e6fd"
          },
            {
                "action": "block",
                "label": "다시 선택",
                "blockId": "611919b7d919c93e877594f8"
          }
        ]
      }
    }
    else:
        res = {
          "version": "2.0",
          "template": {
              "outputs": [
                      {
                    "basicCard": {
                        "description": textResult,
                        "buttons": [
                            {
                                "action": "block",
                                "label": "일기 상세 조회",
                                "blockId": "61192012defb4e3121f31c01"
                                
                }
              ]
            }
          }       
        ]    
      }
    }
  
    return jsonify(res)


@application.route('/diarysearch2', methods=['POST'])
def dairysearch2():
    conn = pymysql.connect(host = "musicchat.cik9oz7kscya.ap-northeast-2.rds.amazonaws.com",
                           user="jeong",
                           passwd="thwjd71410!",
                           db="musicChat",
                           port=3306,
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)

    cursor = conn.cursor()
    req = request.get_json()
    userid = req["userRequest"]["user"]["id"]
    diaryDateMD = req["action"]["detailParams"]["datetime"]["origin"]
    diaryDateYM = req["action"]["detailParams"]["diaryDate"]["origin"]
    userDateYM = datetime.datetime.strptime(diaryDateYM, "%Y-%m")
    lastMonth = diaryDateMD[5:7]
    lastYear = userDateYM.year
    lastDay = diaryDateMD[8:10]
    
        
    query = """SELECT * FROM musicChat.musicChat WHERE userid=%s AND MONTH(nowdate)=%s AND YEAR(nowdate) = %s AND DAY(nowdate) = %s order by nowdate;"""
    val = (userid, lastMonth, lastYear, lastDay)
    cursor.execute(query, val)
    dataCur = cursor.fetchall()
    textResult = "%s년 %s월 %s의 일기입니다." % (lastYear, lastMonth, lastDay) + '\n' 
    

    for i in dataCur:
        textResult = textResult + "----------------------------------" + '\n'
        textResult = textResult + "날짜 : " + str(i["nowdate"]) + '\n'
        textResult = textResult + "기분 : " + str(i["mainEmo"]) + '\n'
        textResult = textResult + "일기 : " + str(i["diary"]) + '\n'
        
    if not dataCur:
        textResult = "선택하신 날짜에 조회할 일기가 없습니다."
    
    conn.close()
    res = {
          "version": "2.0",
         "template": {
              "outputs": [
                      {
                    "simpleText": {
                        "text": textResult
                    
                      }
                  }  
                ], "quickReplies": [
            {
                "action": "block",
                "label": "처음으로",
                "blockId": "61181c9725cb590ace33e6fd"
            },
            {
                "action": "block",
                "label": "일기 조회 처음으로",
                "blockId": "611919b7d919c93e877594f8"
            },
            {
                "action": "block",
                "label": "다른 날짜 일기 조회",
                "blockId": "61192012defb4e3121f31c01"
          }
        ]
      }
    }

    return jsonify(res)


@application.route('/diaryremove', methods=['POST'])
def dairyremove():
    conn = pymysql.connect(host = "musicchat.cik9oz7kscya.ap-northeast-2.rds.amazonaws.com",
                           user="jeong",
                           passwd="thwjd71410!",
                           db="musicChat",
                           port=3306,
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)

    cursor = conn.cursor()
    req = request.get_json()
    userid = req["userRequest"]["user"]["id"]
    removeAgreement = req["action"]["detailParams"]["removeAgreement"]["value"]
    resultText = "일기 삭제가 취소되었습니다."

    if removeAgreement == "yes":
        query = """DELETE FROM musicChat.musicChat WHERE userid=%s;"""
        val = (userid)
        cursor.execute(query, val)
        conn.commit()
        conn.close()
        resultText = "현재까지 작성한 일기 내용이 모두 삭제되었습니다."
        
    res = {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "simpleText": {
              "text": resultText       
            }
          }  
        ],
        "quickReplies": [
          {
            "action": "block",
            "label": "처음으로",
            "blockId": "61181c9725cb590ace33e6fd"
          }
        ]
      }
    }

    return jsonify(res)


@application.route("/monthly", methods=["POST"])
def monthly():
    conn = pymysql.connect(host = "musicchat.cik9oz7kscya.ap-northeast-2.rds.amazonaws.com",
                           user="jeong",
                           passwd="thwjd71410!",
                           db="musicChat",
                           port=3306,
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    req = request.get_json()
    now = datetime.datetime.now()
    month = now.strftime('%Y-%m')
    query = """SELECT satisSong
FROM musicChat.musicChat
WHERE nowdate LIKE %s AND satisSong NOT IN ("0") AND satisSong IS NOT NULL
GROUP BY satisSong ORDER BY COUNT(satisSong) DESC LIMIT 3;"""
    cursor.execute(query, (month + '%'))
    selects = cursor.fetchall()
    conn.commit()

    SongLocation = pd.read_csv ('./SongLocation.csv')
    rank = pd.DataFrame()
    print(selects)
    for i in range(3):
        rank = rank.append(SongLocation.loc[SongLocation['SongNum'] == int(selects[i]['satisSong'])])
    rank = rank.reset_index(drop=True)
    
    res = {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "simpleText": {
              "text": "지난 한 달간 가장 만족도가 높았던 추천곡들이에요. "
            }
          },
          {
            "listCard": {
              "header": {
                "title": "온쉼표 차트"
              },
              "items": [
                {
                  "title": "🥇 " + rank['SongName'][0],
                  "description": rank['Singer'][0],
                  "imageUrl": "https:" + str(rank['Image'][0]),
                  "link": {
                    "web": "http://mw.genie.co.kr/detail/songInfo?xgnm="+str(rank['SongNum'][0])
                  }
                },
                {
                  "title": "🥈 " + rank['SongName'][1],
                  "description": rank['Singer'][1],
                  "imageUrl": "https:" + str(rank['Image'][1]),
                  "link": {
                    "web": "http://mw.genie.co.kr/detail/songInfo?xgnm="+str(rank['SongNum'][1])
                  }
                },
                {
                  "title": "🥉 " + rank['SongName'][2],
                  "description": rank['Singer'][2],
                  "imageUrl": "https:" + str(rank['Image'][2]),
                  "link": {
                    "web": "http://mw.genie.co.kr/detail/songInfo?xgnm="+str(rank['SongNum'][2])
                  }
                }
              ]
            }
          }
        ],
        "quickReplies": [
          {
            "action": "block",
            "label": "처음으로",
            "blockId": "61181c9725cb590ace33e6fd"
          }
        ] 
      }
    }
    return jsonify(res)

if __name__ == "__main__":
    application.run(host='0.0.0.0')