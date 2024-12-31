# 스마트 공장 제품 품질 상태 분류 AI

## 데이터 소개
사용한 데이터는 LG에이머스에서 사용한 데이터로 0, 2로 표현한 부적합 제품과 1로 표현한 적합 제품이 나타나 있다.
데이터는 총 598개의 행과 2881개의 열로 구성되어있다. 

## 전처리
1. 결측값 및 변수 처리
  -모든 열의 값이 nan인 열은 제거
  -열의 값이 하나인 열은 제거
  -변수에 결측값이 있는 경우 변수의 평균값으로 대체  

2. EDA 이후 train data를 line의 분포를 기준으로 구분

3. Standard scaler를 이용한 scailing

## 분석
1. H2O AUTO ML을 이용한 모델링 진행

### LINE1
![image](https://github.com/user-attachments/assets/7412b615-556e-4d12-86fd-531ae8e22c72)
![image](https://github.com/user-attachments/assets/e4255bc6-503f-406a-bff5-765d8478b95a)
![image](https://github.com/user-attachments/assets/4ce11b90-c882-4e86-b43a-16b8c818c41d)

### LINE2
![image](https://github.com/user-attachments/assets/7b3c701a-7c8c-47e8-91e6-ad034622e450)
![image](https://github.com/user-attachments/assets/d75126ec-1fe1-408d-a217-23b2530e3412)
![image](https://github.com/user-attachments/assets/a93e6435-bf2a-47ca-b748-4dfa0f8a6cf9)

### PCA
이 데이터는 많은 열이 있으므로 차원축소도 고려하여 분석을 실행했다.

### PCA LINE1
![image](https://github.com/user-attachments/assets/23a8b6ff-e105-49e4-8723-0f9c1214de0f)
![image](https://github.com/user-attachments/assets/541b7ea4-0f04-4df8-bc61-38178a1c6046)

### PCA LINE2
![image](https://github.com/user-attachments/assets/ead8ca93-0031-46f4-b33b-d99321c7833e)
![image](https://github.com/user-attachments/assets/a7f8bc29-a691-4be0-bc87-7f975088fecd)
![image](https://github.com/user-attachments/assets/53bdc5a3-597c-4822-84fc-bdda646ab4a5)

## 보완점

1. model을 test에 적용시키지 못하여 정확한 성능을 파악하지 못한 것
2. best model만 찾을 뿐 더 상세한 modeling은 하지 못한 것





