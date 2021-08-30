# 온쉼표\_감정기반 음악추천봇

[온쉼표 챗봇 바로가기](https://pf.kakao.com/_Vxexcvs)  
<br />
## 정의
온쉼표는 음악의 한마디를 쉬는 온쉼표라는 단어에서 착안하여,  
**'온전히 쉰다'** 라는 뜻을 담고 있는 가사 기반 음악 추천 서비스입니다.  
사용자가 챗봇과 대화하면서 전달하는 감정 일기를 분석하여,  
그 날 그 순간 사용자의 감정과 가장 적합한 가사를 가진 음악을 추천합니다.  
<br />

## 기능
**✔ 감정 일기로 노래 추천**  
<p align="center"><img width="300" src="https://user-images.githubusercontent.com/57048162/131371045-6117b254-b5c5-43df-849c-d0886f98dcd1.gif" /></p>  

>사용자가 그 날의 감정과 감정 일기를 작성하면  
>분석하여 사용자의 감정과 어울리는 가사의 노래를 추천

<br />

**✔ 간단한 감정 입력으로 노래 추천**  
<p align="center"><img width="300" src="https://user-images.githubusercontent.com/57048162/131367467-343323bd-197c-4201-b765-be5d3e8dfbd3.gif" /></p>  

>감정 일기를 작성하지 않고, 사용자의 감정만 간단히 입력하여  
>감정에 어울리는 노래를 추천

<br />

**✔ 일기 조회/삭제 기능**  
<p align="center"><img width="300" src="https://user-images.githubusercontent.com/57048162/131371209-5f401f09-1533-4df5-9cef-75569ac9fa55.gif" /></p>  

>일기 조회 : 사용자가 원하는 날짜의 일기 조회 기능  
>일기 삭제 : 현재까지의 모든 일기 데이터 삭제 기능

<br />

**✔ 온쉼표 차트**  
<p align="center"><img width="300" src="https://user-images.githubusercontent.com/57048162/131369219-810df80b-aee7-4385-b080-1666ce59062e.gif" /></p>  

>지난 한 달간 사용자가 가장 만족한 곡 3곡을 조회할 수 있는 기능  

<br />

## 기술 스택
<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=white"/>&nbsp
  <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=Flask&logoColor=white"/>&nbsp
  <img src="https://img.shields.io/badge/AWS EC2-232F3E?style=flat-square&logo=AmazonAWS&logoColor=white"/>&nbsp
  <img src="https://img.shields.io/badge/AWS RDS-232F3E?style=flat-square&logo=AmazonAWS&logoColor=white"/>&nbsp
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=MySQL&logoColor=white"/>&nbsp
  <img src="https://img.shields.io/badge/Kakao i-FFCD00?style=flat-square&logo=kakaoTalk&logoColor=white"/>
</p>  <br />
    
## 프로젝트 설명
### 1. 감성 사전  
- Thayer가 제안한 모델을 일부 변형하여 재정의 후 감정어 분류  
![image](https://user-images.githubusercontent.com/57048162/131365866-24fec3a0-d71d-467d-82a7-e84ad3c25f6d.png)  

### 2. 음악 추천
- 작성된 코드를 이용하여 텍스트 감정 분석 후 음악 추천
  - 메인 감정과 일기 감정이 서로 ±1 카테고리 범위 내에 존재 or 일기 감정만 분석 가능  
    ⇒ 일기감정 좌표에서 가장 가까운 음악 추천
  - 인접하지 않거나 메인 감정만 분석 가능  
    ⇒ 메인 감정 카테고리와 같은 음악 랜덤 추천
  - 두 감정 모두 분석 불가능  
    ⇒ 감정어가 5개 이하인 음악 랜덤 추천  


 
![image](https://user-images.githubusercontent.com/57048162/131367012-a1da2413-782e-4ca8-ad4f-620159be232f.png)



### 3. 함수 소개
**<main. py>** 
- chatDB(result) : 곡 추천 후 만족한 곡까지 DB에 저장하는 함수
- diarymusic() : 곡 추천 함수
- feedback() : 피드백까지 받게 되면 DB에 피드백과 열람 동의 여부를 저장하는 함수
- feelmusic() : 간단 곡 추천 함수
- diarysearch1() : 일기 월별 열람 함수 
- diarysearch2() : 일기 일별 열람 함수
- diaryremove() : 일기 삭제 함수
- monthly() : 온쉼표 차트 함수, 지난 달 사용자들이 추천받은 뒤 선택한 만족한 곡 중 상위 3곡을 보여주는 함수
  
**<mrp.py>**  
- emotionAnalysis(diary) : 사용자 감정 분석 함수
- SelectCategory(x, y) : 좌표를 통해 감정 카테고리 판단하는 함수
- resultCheck(feelX, feelY, diaryX, diaryY) : 감정 분석 결과를 통해 음악 추천 방식을 결정하는 함수
- musicRecommend(diaryX, diaryY) : 사용자 감정에 가장 근접한 음악 추천 함수
- randomMusic(cateNum) : 랜덤 음악 추천 함수
  
**<lyrics_analysis.py>**  
- LyricsEmotion(ly) : 가사의 감정값을 분석하는 함수
- SelectCategory(x, y) : 좌표를 통해 카테고리를 결정하는 함수
  
**<lyrics_crawl.py>**  
- 지니뮤직에서 가사를 크롤링해주는 코드  

<br />

## 참고 자료
- 문창배 외 3.(한국산업정보학회). 『음악추천을 위한 분위기 태그 분석』
- 신기원 외3.(한국지능정보시스템학회). 『감정 온톨로지를 활용한 가사 기반의 음악 감정 추출』

