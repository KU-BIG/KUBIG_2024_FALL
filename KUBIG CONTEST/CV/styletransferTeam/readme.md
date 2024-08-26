# 동양화 - 서양화 화풍 변경 생성 모델

팀명: 김모네

<br>
CV 팀원: 18기 심서현 / 20기 김민재 / 20기 이정제
<br>



<br>
<br>

## Model
CycleGAN, VGG19

<img width="500" alt="image" src="https://github.com/user-attachments/assets/2e1bc073-abba-4ff2-a812-58e8a265f24a">


<img width="500" alt="image" src="https://github.com/user-attachments/assets/05ec4e00-850a-4412-aa66-af132d5116fa">


CycleGAN: 두 가지 서로 다른 도메인 간의 이미지 변환을 학습하는 모델, 한국화 서양화 화풍변환에 유리하다고 판단하여 모델로 선정

VGG19: 이미지의 다양한 층에서 feature map을 추출하기 용이한 모델, 원본 이미지의 구조적 요소를 유지하면서도, 스타일 이미지의 텍스처와 색상을 효과적으로 적용 가능한 모델



## Dataset
### 동양화(풍경화)
 -  한국 전통 수묵화 화풍별 제작 데이터
   
<img width="600" alt="image" src="https://github.com/user-attachments/assets/661eb456-20aa-4155-9db0-3195235874ed">


### 서양화(풍경화)
 - 클로드 모네 풍경화

<img width="600" alt="image" src="https://github.com/user-attachments/assets/e194be5c-512f-4688-b27f-d80c4bc35f89">
  
### 동양화(초상화)
 - 각종 동양 초상화와 어진
   
<img width="600" alt="image" src="https://github.com/user-attachments/assets/b74a204f-8768-47d4-9dde-f827955f4b15">

### 서양화(초상화)
 - 각종 서양 초상화

<img width="600" alt="image" src="https://github.com/user-attachments/assets/4202f83f-66c3-48ed-9afe-d234c3bda7b6">

# Result
  
## 동양화 to 서양화(풍경화)

<img width="800" alt="image" src="https://github.com/user-attachments/assets/bd13cf38-526b-4e73-aea0-ecd7166c7b70">

CycleGAN을 이용한 결과물이며, 학습에는 수묵화 계열의 동양화와 모네의 풍경화를 학습하였다.

두 한국 풍경화 수묵화 계열로 흑백으로 그려진 그림이다. 이를 모네의 화풍으로 변경시켜본 결과, 색을 입혔으며 모네의 유화적 질감을 잘 반영했다고 보여진다.




## 동양화 to 서양화(초상화)

<img width="800" alt="image" src="https://github.com/user-attachments/assets/a2d465ad-5562-45ad-a78a-903ea2920ff4">

<img width="800" alt="image" src="https://github.com/user-attachments/assets/c150d0d8-1985-4e28-a2dc-a73efe7f5c07">

VGG19을 이용한 결과물이다.

처음에 보이는 이미지는 왼쪽이 화풍을 변경 할 김홍도 자화상과 세종대왕 어진, 왼쪽은 클로드 모네의 자화상으로 이 모네의 자화상의 화풍으로 김홍도 자화상의 화풍을 변경해보았다.
결과는 오른쪽 이미지, 클로드 모네의 특유의 즉흥적이고 빠른 붓질이 잘 적용되었다는 것을 확인할 수 있다.




## 서양화 to 동양화(풍경화)

<img width="600" alt="image" src="https://github.com/user-attachments/assets/e003fd4d-1d1c-483e-85c7-1d1343f3f1d8">

<img width="600" alt="image" src="https://github.com/user-attachments/assets/b9732216-c603-4618-86ef-47c869c7cad4">

왼쪽이 원본인 모네의 그림. 오른쪽이 변환된 이미지

육지 부분을 표현 시 수묵화 특유의 거친 붓터치로 바위산을 표현하는데 성공. 

수묵화의 종이 질감으로 배경을 재현

색이 많이 사용되거나 채도가 높은 경우 누르스름한 종이 효과를 채택해 구현하는 모습을 볼 수 있었음

원본의 나무를 수묵화 방식으로 재현. 



## 서양화 to 동양화(초상화)

<img width="700" alt="image" src="https://github.com/user-attachments/assets/29ef0f01-4d65-4a75-b912-d7ebeb935e19">

<img width="470" alt="image" src="https://github.com/user-attachments/assets/fb77bdc6-53db-4ead-a711-82f7515a6ad8">

초상화에 모델 적용 시, 서양화에서 보이는 붓터치 자국을 수묵화 및 조선시대 초상화처럼 수정해서 성공적으로 재현함.

얼굴 형태를 표현할 때 잔주름이나 음영을 생략해서 표현. 조선시대 초상화의 특징을 반영한 것으로 보임




KUBIG contest

