![Major-event traffic delay analysis](assets/project-hero.svg)

<div align="center">

**대형 행사 뒤 이동이 왜 오래 걸렸는지 데이터로 확인하고, 수요 분산과 셔틀 운영 시나리오로 연결했습니다.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Analysis](https://img.shields.io/badge/Analysis-OD%20%2B%20Transit%20Supply-0F766E)
![Model](https://img.shields.io/badge/Model-Isotonic%20Regression-D97706)
![Tests](https://img.shields.io/badge/Tests-pytest-7C3AED)

교내 데이터 분석 프로젝트 우수상

[분석 결과](#분석-결과) · [분석 흐름](#분석-흐름) · [실행](#실행) · [검증 범위](#검증-범위)

</div>

## 출발점

여의도 불꽃축제가 끝난 뒤 평소보다 귀가 시간이 오래 걸린 경험에서 시작했습니다. "사람이 많이 와서 혼잡했다"는 설명만으로는 언제, 어느 방향에 교통 수단을 더 투입해야 하는지 알 수 없습니다.

SKT OD와 체류인구, 버스와 지하철 승하차, TPSS 정차횟수, 정류장과 노선 공간정보를 결합해 행사일의 수요와 대중교통 공급 상태를 함께 살펴봤습니다.

## 분석 흐름

~~~mermaid
flowchart LR
    A["OD, population,<br/>transit data"] --> B["ID and spatial<br/>matching audit"]
    B --> C["Event vs reference<br/>time profiles"]
    C --> D["Demand and supply<br/>proxy comparison"]
    D --> E["Monotonic<br/>delay model"]
    E --> F["Hub shuttle<br/>scenario"]
~~~

### 1. 데이터 결합부터 다시 확인

초기 정류장 ID matching coverage는 약 26.7%였습니다. 이 상태에서는 정류장 단위 결과를 믿기 어려워 bbox, 정류장명, route master, TPSS와 GIS encoding을 다시 확인했습니다.

### 2. 수요만 보던 문제를 바꿈

처음에는 행사 혼잡을 수요 증가로만 설명하려 했습니다. 분석에서는 승객이 늘어난 동시에 차량이 정류장에 관측된 횟수가 줄어드는 방향이 나타났습니다. 실제 공급량을 직접 확보하지 못했기 때문에 TPSS 정차횟수를 공급 상태의 proxy로 사용했습니다.

### 3. 단조 제약을 적용

선형 회귀는 초과 교통량과 지체의 관계를 하나의 기울기로 표현합니다. 데이터에서는 증가 폭이 일정하지 않았고, 교통량이 늘었는데 예측 지체가 줄어드는 구간도 생겼습니다. 증가 폭은 데이터에 맡기되 지체가 감소하지 않도록 Isotonic Regression을 적용했습니다.

## 분석 결과

원 분석의 공통 정류장 비교에서 행사일 승객 수는 참고일 평균보다 약 49,567명 많았고, 정차횟수 proxy는 약 3,488회 적었습니다. 18시부터 23시에도 승객은 약 32,628명 많고 정차횟수는 약 3,610회 적은 방향이 유지됐습니다.

이 수치는 행사 효과의 인과 추정치가 아닙니다. 혼잡을 수요 증가 하나가 아니라 수요와 공급 proxy가 함께 움직인 운영 불균형으로 다시 보게 만든 탐색 결과입니다.

분석 결과는 모든 목적지로 직접 운행하는 노선 대신 공덕, 당산, 노량진 환승거점까지 연결하는 셔틀 시나리오로 이어졌습니다. 45석 x 100대 x 3회전은 최대 13,500명의 수송 규모를 비교한 산술 예시이며 최적 배차 결과는 아닙니다.

## 실행

~~~bash
python -m pip install -e ".[dev]"
pytest
python scripts/run_sample_analysis.py
~~~

원본 데이터는 이용 조건과 용량 문제로 포함하지 않았습니다. 같은 열 구조를 가진 synthetic sample로 전처리, 비교, 날짜 단위 검증과 시나리오 계산을 실행할 수 있습니다.

| 행사일과 참고일 profile | 단조 제약 모델 |
|---|---|
| ![Synthetic event and reference profiles](results/sample/event_vs_baseline.png) | ![Synthetic isotonic delay example](results/sample/demand_delay_curve.png) |

위 그림은 코드 경로를 보여주는 synthetic example이며 실제 축제 결과나 모델 성능이 아닙니다.

## 저장소 구성

~~~text
data/sample/             synthetic input
notebooks/               public EDA and model validation
src/event_traffic/       preprocessing, modeling, scenario
scripts/                 sample pipeline entry point
results/sample/          generated tables and figures
tests/                   preprocessing and model tests
~~~

## 검증 범위

- 행사일은 2023년 10월 7일 토요일이고 참고일 6개는 일요일입니다. 원 노트북의 "평상시 토요일" 표기를 수정했으며, 비교 결과에는 요일 차이가 섞여 있습니다.
- 행사일 한 번의 관측만으로 일반적인 행사 효과를 추정할 수 없습니다.
- Isotonic Regression은 단조 관계를 표현하지만 인과 효과를 추정하지 않습니다.
- 셔틀 계산은 수송 규모를 비교한 시나리오입니다. 배차, 도로 운영과 비용 효과를 검증한 simulation은 아닙니다.

[Notebook audit](docs/NOTEBOOK_AUDIT.md) · [Data guide](data/README.md) · [Follow-up plan](docs/LEARNING_ROADMAP.md)
