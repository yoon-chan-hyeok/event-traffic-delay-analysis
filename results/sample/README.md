# 합성 샘플 결과

이 폴더는 `python scripts/run_sample_analysis.py`를 실행하면 다시 생성됩니다.

- `event_vs_baseline.csv`: 합성 행사일과 세 참고일의 시간대별 비교
- `model_validation.csv`: 합성 날짜를 하나씩 제외한 모델 비교
- `out_of_fold_predictions.csv`: held-out 날짜별 예측
- `scenario_summary.json`: 45석, 100대, 3회전 시나리오 계산
- PNG 두 개: 파이프라인 출력 형식 확인용 그래프

CSV와 그림의 수치는 실제 여의도 관측값이 아닙니다. 이 결과로 축제 효과, 지체시간 또는 모델 성능을 주장하지 않습니다.
