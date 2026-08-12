# 미구현 데이터·분석 확장 계획

아래 항목은 현재 공개 case study에 포함되지 않은 후속 작업입니다.

## 재현 가능한 데이터 처리

- raw, clean, mart 계층과 data dictionary
- schema, 범위, 결측과 좌표계·시간대 검증
- 공개 synthetic data로 실행되는 pipeline과 lineage

## 분석과 전달

- 여러 동요일과 비행사일 baseline 비교
- 시간·공간 단위 sensitivity analysis와 준실험 설계
- 효과크기, 신뢰구간과 잔차 진단
- 비용, 수송량과 회전시간을 조절하는 scenario calculator

완료 기준은 공개 synthetic pipeline, 자동 분석 리포트, scenario demo와 CI data test입니다.
