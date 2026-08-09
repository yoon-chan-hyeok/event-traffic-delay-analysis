# Learning & Engineering Roadmap

## 1. 재현 가능한 데이터 파이프라인

- raw/clean/mart 계층과 명시적인 데이터 dictionary
- Pandera 또는 Great Expectations 기반 schema·범위·결측 검증
- 공간 좌표계, 시간대, 행정동 코드 변경 테스트
- 증분 처리와 캐시로 대용량 파일 재실행 비용 절감

**완료 증거:** 공개 합성 데이터로 끝까지 실행되는 pipeline과 data lineage

## 2. 분석 신뢰성

- 여러 동요일·비행사일 baseline 비교
- 시간대·공간 단위 변화에 대한 sensitivity analysis
- 공변량을 포함한 회귀와 준실험 설계 학습
- 효과크기, 신뢰구간, 잔차 진단 제공

**완료 증거:** 가정·한계가 자동 포함되는 분석 리포트

## 3. 전달과 운영

- EDA → 가설 → 운영안으로 이어지는 dashboard
- 비용, 수송량, 회전시간을 조절하는 scenario calculator
- Docker 환경과 CI 데이터 테스트

**완료 증거:** 공개 demo와 의사결정자가 읽을 수 있는 1-page brief

