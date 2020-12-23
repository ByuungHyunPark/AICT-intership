# SNUH Medical AI Challenge 2020
##### VitalDB를 활용한 수술중 저혈압 예측 (동맥압 파형 데이터를 통해 5분 후의 저혈압 예측)
- http://maic.or.kr/competitions/1/leader-board
  - 대회기간 : 2020/09/01 ~ 2020/10/31
- 파형의 Raw 데이터를 조건에 맞게 Labeling 및 학습을 위한 데이터 구축과정도 진행
  - 의료 도메인지식이 부족하여 이해하는데에 있어서 상당히 어려움을 겪음
- 평가지표 : AUPRC, AUROC
- 최종 AUPRC : 0.4564 / AUROC : 0.9161 (22/36등)
- CNN, LSTM , LightGBM, WaveNet 등 다양한 모델링 적용
- 대부분 비슷한 성능을 나왔음 , LightGBM이 근소하게 높은 결과를 보임
