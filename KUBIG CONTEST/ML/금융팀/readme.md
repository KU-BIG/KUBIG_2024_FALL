# 자동차 보험 사기 탐지 및 네트워크 분석

<img width="669" alt="스크린샷 2024-08-28 오후 3 24 45" src="https://github.com/user-attachments/assets/0b632442-095d-475e-ba32-a6e0e4c745ea">

### 프로젝트 목표
1. 보험 사기를 탐지하는 분류 알고리즘 개발
2. 네트워크 분석을 결합해 노드별 사기 가능성을 평가하고 기존 머신러닝 모델과의 성능 비교

### 데이터셋 및 논문
[Dacon 자동차 보험사기 탐지 데이터셋](https://dacon.io/competitions/official/236282/overview/description)

[네트워크 분석 논문: 'Social Network Analytics for Supervised Fraud Detection in Insurance'](https://onlinelibrary.wiley.com/doi/10.1111/risa.13693)

## 머신러닝 베이스라인 
### 실험 결과
<img width="601" alt="image" src="https://github.com/user-attachments/assets/d38ae18f-3bae-4be4-8f71-0f046de39c2d">

결측치 drop, 이상치 처리 X, 파생변수 3가지 추가(payout_vs_avg 제거), SMOTE 오버샘플링, correlation 0.9 이상의 변수 제거의 조합으로 나온 **accuracy 0.8949인 최적의 모델 CatBoost를 Baseline으로 설정**

### 변수 중요도
<img width="746" alt="image" src="https://github.com/user-attachments/assets/27b9f09b-bc7e-49a2-9254-922670e2db4f">

네트워크 분석의 party 노드로 중요 변수 상위 3개를 선정 
- age of vehicle: 자동차 연식
- claim frequency factor: 자동차 연식 대비 보험 청구 횟수 비율, (past_num_of_claims) / (age_of_vehicle)
- past num of claims: 보험 청구 횟수

## 네트워크 분석
### 노드 정의
#### 기존 논문의 노드 정의
- Group 1: 청구(claims, C)
- Group 2: 당사자(parties, P)
  - P1: 계약자(Policyholder)
  - P2: 중개인(Broker)
  - P3: 전문가(Expert)
  - P4: 정비소(Garage)
 
#### 본 프로젝트의 노드 정의
- Group 1: 청구(claims, C)
- Group 2: 자동차 연식(age of vehicle), 보험 청구 횟수(past num of claims), claim frequency factor(연식에 따른 청구 횟수)


**=> 각 변수에서 범주를 만든 후 각 범주를 하나의 당사자(party)에 대응**

### BiRank 알고리즘
그 후 bipartite network를 구성해 청구 노드, 당사자 노드별로 사기 점수를 계산
1. 각 청구(C)에 해당되는 범주(P)와 연결하여 네트워크 구성
2. 사기 점수 초기화
3. 정규화된 엣지 가중치 계산
4. 사기 청구 정보 벡터 정의
5. BiRank 알고리즘으로 사기 점수 계산. 점수 계산을 반복하며 사기 노드(fraud = 1)인 경우 점수를 더 높게 부여함.

### 사기 점수 통계 계산
<img width="1128" alt="image" src="https://github.com/user-attachments/assets/f47a0b73-ddea-4640-aa90-a0eed953b4a1">

- birank_score: BiRank 알고리즘에 의해 계산된 각 노드(청구)의 사기 가능성 점수.
- n1_q1, n1_med, n1_max : 노드의 1차 이웃에서의 BiRank 점수의 하위 25%, 50%, 최대값
- n2_q1, n2_med, n2_max: 노드의 2차 이웃에서의 BiRank 점수의 하위 25%, 50%, 최대값
- n1_size, n2_size : 노드의 1차/2차 이웃의 크기
- n2_ratioFraud, n2_ratioNonFraud: 노드의 2차 이웃 중 사기/비사기 청구의 비율
- n2_binFraud: 노드의 2차 이웃에 사기 청구가 존재하는지 여부를 나타내는 이진 값 (1은 사기 청구가 존재, 0은 존재하지 않음)

## ML 모델 & 네트워크 분석 비교
<img width="489" alt="스크린샷 2024-08-28 오후 3 41 33" src="https://github.com/user-attachments/assets/226c8b6b-9f8f-4110-adfe-41ee58feff1b">

**네트워크 분석 결과를 추가한 모델의 성능이 가장 우수하나(accuracy=0.8994) 기존 모델과 미세한 차이를 보이고 있다.**

## 결론
### 네트워크 분석의 의의
- 데이터 간의 연결성을 고려한 네트워크 분석을 직접 시도
- 보험사, 금융 회사 등에서 자주 이뤄지는 사기 탐지 업무에 있어 단순히 ML을 뛰어넘은 추가 분석을 진행

### 프로젝트의 한계
- 사회 연결망을 표현하는 논문의 의도대로 적용하지 못함 (데이터셋의 한계)
- 그럼에도 불구하고 약간의 성능 향상을 발견
- 만약 데이터셋이 다양한 party를 포함해 social network를 만들 수 있었다면 실제로 더 높은 성능 향상을 기대해볼 수 있음

