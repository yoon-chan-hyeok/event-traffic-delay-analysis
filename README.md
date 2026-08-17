![Major-event traffic delay analysis](assets/project-hero.svg)

<div align="center">

**대형 행사 뒤 이동 지연을 수요와 대중교통 공급 proxy로 나눠 보고, 데이터 결합과 비교 설계의 한계까지 점검했습니다.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Analysis](https://img.shields.io/badge/Analysis-OD%20%2B%20Transit%20Supply-0F766E)
![Model](https://img.shields.io/badge/Model-Isotonic%20Regression-D97706)
![Tests](https://github.com/yoon-chan-hyeok/event-traffic-delay-analysis/actions/workflows/ci.yml/badge.svg)

교내 데이터 분석 프로젝트 우수상

[분석 내용](#분석-내용) · [모델링](#모델링) · [실행](#실행) · [검증 범위](#검증-범위)

</div>

## 출발점

여의도 불꽃축제가 끝난 뒤 평소보다 귀가 시간이 오래 걸린 경험에서 시작했습니다. "사람이 많이 와서 혼잡했다"는 설명만으로는 언제, 어느 방향에 교통 수단을 더 투입해야 하는지 알기 어렵습니다.

SKT OD와 체류인구, 버스와 지하철 승하차, TPSS 정차횟수, 정류장과 노선 공간정보를 결합해 행사일의 수요와 대중교통 공급 상태를 함께 살펴봤습니다.

## 분석 내용

```mermaid
flowchart LR
    A["OD, population,<br/>transit data"] --> B["ID and spatial<br/>matching audit"]
    B --> C["Event vs reference<br/>time profiles"]
    C --> D["Demand and supply<br/>proxy comparison"]
    D --> E["Grouped validation<br/>and monotonic model"]
    E --> F["Hub shuttle<br/>capacity scenario"]
```

| 데이터 | 분석에서 맡은 역할 | 결합 시 확인한 것 |
|---|---|---|
| OD | 시간대별 이동 수요 | 출발지, 도착지, 시간 단위 |
| 체류인구 | 행사장 주변 인구 변화 | 공간 범위와 기준 시점 |
| 버스·지하철 승하차 | 대중교통 이용 변화 | 정류장·역 ID와 시간대 |
| TPSS 정차횟수 | 공급 상태 proxy | 정류장과 노선 matching |
| GIS | 정류장과 노선 공간 관계 | 좌표계, bbox, encoding |

### 데이터 결합부터 다시 확인

초기 정류장 ID matching coverage는 약 26.7%였습니다. 이 상태에서는 정류장 단위 결과를 믿기 어려워 bbox, 정류장명, route master, TPSS와 GIS encoding을 다시 확인했습니다.

TPSS 정차횟수는 실제 배차량이나 공급량이 아닙니다. 차량이 정류장에 관측된 상태를 나타내는 proxy로만 사용했습니다.

### 수요만 보던 문제를 바꿈

처음에는 행사 혼잡을 수요 증가로만 설명하려 했습니다. 원 분석에서는 승객이 늘어난 동시에 차량이 정류장에 관측된 횟수가 줄어드는 방향이 나타났습니다. 실제 공급량을 직접 확보하지 못했기 때문에 TPSS 정차횟수를 공급 상태의 proxy로 사용했습니다.

## 모델링

선형 회귀는 초과 교통량과 지체의 관계를 하나의 기울기로 표현합니다. 데이터에서는 증가 폭이 일정하지 않았고, 교통량이 늘었는데 예측 지체가 줄어드는 구간도 생겼습니다.

Isotonic Regression을 선택한 이유는 증가 폭을 데이터에 맡기면서 초과 교통량이 늘 때 예측 지체가 감소하지 않는 단조 조건을 반영하기 위해서입니다.

공개 pipeline은 mean baseline, linear regression과 isotonic regression을 날짜 단위 holdout으로 비교합니다. Held-out date의 관측은 model fitting에서 모두 제외하며 signed delay도 임의로 버리지 않습니다.

Isotonic Regression은 관계의 형태를 표현할 뿐 행사로 인한 인과 효과를 추정하지 않습니다.

## 현재 결론

원 분석에서는 행사 시간대에 수요가 늘고 TPSS 정차횟수 proxy가 줄어드는 방향이 함께 나타났습니다. 하지만 행사일은 토요일이고 참고일 6개는 일요일이어서 당시 계산한 차이를 행사 효과나 대표 결과로 사용하지 않습니다.

현재 남길 수 있는 결론은 두 가지입니다.

1. 수요 자료만으로 혼잡을 설명하지 않고 공급 상태를 나타내는 proxy를 함께 봐야 합니다.
2. 여러 교통 데이터를 결합할 때는 모델링보다 ID, 공간 범위와 날짜 비교 조건의 검증이 먼저입니다.

원 분석은 모든 목적지로 직접 운행하는 노선 대신 공덕, 당산, 노량진 환승거점까지 연결하는 셔틀 아이디어로 이어졌습니다. 공개본의 수송량 계산은 대안의 규모를 비교하는 산술 시나리오이며 최적 배차나 비용 효과를 검증한 결과가 아닙니다.

## 분석을 다시 점검한 이유

이벤트 날짜는 2023년 10월 7일 토요일입니다. 기존 노트북에서 "평상시 토요일"로 설명한 참고일 6개는 실제로 모두 일요일이었습니다. 이전 R²도 필터링한 동일 데이터에 맞춘 in-sample 값이므로 일반화 성능으로 사용할 수 없습니다.

공개본에서는 기존 대표 수치를 제거하고 날짜 단위 holdout을 사용하는 평가 함수를 만들었습니다. Synthetic 결과와 실제 행사 분석도 분리했습니다. 전체 점검 내용은 [Notebook audit](docs/NOTEBOOK_AUDIT.md)에 기록했습니다.

## 실행

```bash
python -m pip install -e ".[dev]"
pytest
python scripts/run_sample_analysis.py
```

원본 데이터와 전체 분석 코드는 이용 조건과 정리 상태 때문에 포함하지 않았습니다. 공개 코드는 같은 열 구조를 가진 synthetic sample로 전처리, 비교, 날짜 단위 검증과 시나리오 계산의 실행 경로를 보여줍니다.

| 행사일과 참고일 profile | 단조 제약 모델 |
|---|---|
| ![Synthetic event and reference profiles](results/sample/event_vs_baseline.png) | ![Synthetic isotonic delay example](results/sample/demand_delay_curve.png) |

위 그림은 코드 경로를 보여주는 synthetic example입니다. 실제 축제 결과나 model 성능이 아닙니다.

## 저장소 구성

```text
data/sample/             synthetic input
notebooks/               public EDA와 model validation
src/event_traffic/       preprocessing, modeling, scenario
scripts/                 sample pipeline entry point
results/sample/          generated table, prediction, figure
tests/                   preprocessing, model, scenario test
```

## 검증 범위

- 행사일 한 번의 관측만으로 일반적인 행사 효과를 추정할 수 없습니다.
- TPSS 정차횟수는 실제 공급량이 아닌 proxy입니다.
- Isotonic Regression은 단조 관계를 표현하지만 인과 효과를 추정하지 않습니다.
- 셔틀 계산은 수송 규모를 비교한 시나리오이며 배차와 비용 효과를 검증하지 않습니다.

[Data guide](data/README.md) · [Notebook audit](docs/NOTEBOOK_AUDIT.md) · [Follow-up plan](docs/LEARNING_ROADMAP.md)
