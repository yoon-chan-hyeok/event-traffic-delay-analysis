![Major-event traffic delay analysis](assets/project-hero.svg)

<div align="center">

# Event Traffic Delay Analysis

**Archived prototype · 여의도 불꽃축제 교통 분석의 초기 설계와 수정 기록**

[최종 실제 데이터 분석](https://github.com/yoon-chan-hyeok/yeouido-festival-mobility-analysis) · [Notebook audit](docs/NOTEBOOK_AUDIT.md) · [실행 방법](#실행)

</div>

> 이 저장소는 별도의 포트폴리오 프로젝트가 아닙니다. 초기 notebook의 비교군 오류를 어떻게 발견했고 분석을 어떻게 다시 설계했는지, 그리고 열 구조를 재현한 synthetic pipeline을 보존한 archive입니다. 현재 결과와 수치는 [Yeouido Festival Mobility Analysis](https://github.com/yoon-chan-hyeok/yeouido-festival-mobility-analysis)를 기준으로 봐주세요.

## 이 저장소가 남아 있는 이유

여의도 불꽃축제 뒤 길어진 귀가 시간을 수요 증가만으로 설명할 수 있는지 확인하려고 시작했습니다. SKT OD와 체류인구, 버스·지하철 이용 자료, TPSS 정차횟수와 공간정보를 결합했지만, 첫 notebook에는 행사일과 비교일의 요일이 맞지 않는 문제가 있었습니다.

잘못된 결과를 그대로 다듬기보다 오류와 수정 과정을 남겼습니다. 이 저장소는 초기 가설과 코드 구조를, 최종 저장소는 같은 요일의 실제 데이터를 다시 계산한 결과를 보여줍니다.

| 구분 | 이 저장소 | 최종 저장소 |
|---|---|---|
| 역할 | 초기 notebook audit와 synthetic 실행 예제 | 실제 데이터 재분석과 공개 결과 |
| 비교 설계 | 토요일 행사일과 일요일 참고일이 섞인 문제 확인 | 행사일과 같은 토요일 비교군 사용 |
| 공개 수치 | 포트폴리오 성과로 사용하지 않음 | 검증된 기술통계와 조건을 함께 공개 |
| 모델 | Isotonic Regression의 설계 예제 | 일반화 근거가 부족해 예측 점수 미공개 |

## 분석을 다시 설계한 지점

### 비교 날짜

행사일은 2023년 10월 7일 토요일이지만 초기 참고일 6개는 일요일이었습니다. 요일 효과가 섞인 기존 차이는 행사 효과로 해석하지 않습니다. 최종 분석에서는 자료별로 실제 토요일 비교군을 다시 구성했습니다.

### 수요와 운행 상태

혼잡을 방문객 증가만으로 설명하지 않기 위해 TPSS 정차횟수를 함께 봤습니다. 다만 이 값은 버스 대수나 좌석 공급량이 아니라 정류장에 기록된 운행횟수 지표입니다. 도로통제, 우회, 무정차나 결행 중 무엇이 변화를 만들었는지도 이 자료만으로는 구분할 수 없습니다.

### 단조 제약 모델

초과 교통량이 늘어날 때 예측 지체가 감소하지 않도록 Isotonic Regression을 적용했습니다. 증가 폭을 하나의 기울기로 고정하지 않으면서 교통 지체의 방향성은 지키려는 선택이었습니다. 하지만 기존 결과는 비교 날짜와 검증 설계에 문제가 있어 예측 성능의 근거로 사용하지 않습니다.

### 환승거점 셔틀

공덕·당산·노량진까지 단거리 셔틀을 연결하는 아이디어와 수송 규모 계산도 남아 있습니다. 이는 대안의 구조를 살펴본 산술 시나리오이며, 최적 입지·배차·비용 효과를 검증한 정책 결과가 아닙니다.

## 실행

```bash
python -m pip install -e ".[dev]"
pytest
python scripts/run_sample_analysis.py
```

공개 코드는 실제 관측값이 아니라 같은 열 구조를 가진 synthetic sample을 사용합니다. 아래 그림도 실행 경로를 확인하기 위한 예제입니다.

| 행사일과 참고일 profile | 단조 제약 모델 |
|---|---|
| ![Synthetic event and reference profiles](results/sample/event_vs_baseline.png) | ![Synthetic isotonic delay example](results/sample/demand_delay_curve.png) |

## 저장소 구성

```text
data/sample/             synthetic input과 데이터 안내
notebooks/               공개 EDA와 모델 검증 예제
src/event_traffic/       전처리, 모델링과 시나리오 코드
scripts/                 sample pipeline 실행 파일
results/sample/          synthetic 결과 표와 그림
tests/                   전처리와 모델 단위 테스트
docs/NOTEBOOK_AUDIT.md   원 notebook 오류와 해석 범위
```

최종 실제 데이터 분석에서는 같은 요일 비교, OD 통행량 가중평균, 공간 결합률, 30분 구간 파싱과 공개 수치 재현을 다시 검증했습니다.
