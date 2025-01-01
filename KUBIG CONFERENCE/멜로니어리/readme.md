## [추천시스템] 멜로니어리 

## Members

20기 김유진, 김재훈, 박준희 

## Introduction 

오늘의 일기와 간단한 음악 취향을 입력하면, \#오늘 \#듣기 \#좋은 \#노래 리스트를 출력해주는 알고리즘 디자인 

## Data

##### Melon Crawling
- 인기차트
- 장르음악
- 멜론 DJ 플레이리스트 

## Modeling

##### 일기 태그 추출 
- OpenAI 활용
- 키워드 3개, 감정 3개 추출 

## Modeling

##### 일기 태그 추출 Tagging
- OpenAI 활용
- 키워드 3개, 감정 3개 추출

##### 벡터화 Word Embedding
- fastText Korean Pretrained Model 활용 
- 유사 단어 검색, 가사-태그리스트 벡터화

##### 취향 필터링 Filtering
- 장르, 대중성, 최신가요 선호도의 정보를 받아 1차 곡 필터링
