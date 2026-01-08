# Task ID: 2

**Title:** SQL Agent 평가 시스템 구현

**Status:** pending

**Dependencies:** None

**Priority:** high

**Description:** SQL Agent의 Execution Accuracy를 측정하기 위한 자동 평가 시스템 구축

**Details:**

## 구현 세부사항

### 1. SQL 평가 데이터셋 생성
- `data/evaluation/sql_eval_dataset.json` 파일 생성
- 최소 20개의 질문-예상SQL-예상결과 쌍
- 다양한 난이도 포함:
  - 단순 SELECT (5개)
  - JOIN 쿼리 (8개)
  - GROUP BY/집계 함수 (5개)
  - 복잡한 서브쿼리 (2개)

### 2. 평가 메트릭 정의
#### Execution Accuracy
- 생성된 SQL이 에러 없이 실행되는 비율
- `성공 건수 / 전체 건수 * 100`

#### Result Accuracy
- 실행 결과가 예상 결과와 일치하는 비율
- 허용 오차: 숫자 ±1%, 문자열 완전 일치

### 3. 평가 스크립트 작성
- `scripts/evaluate_sql.py` 생성
- SQLAgent에 질문 입력 → SQL 생성 → 실행 → 결과 비교
- Self-Correction 재시도 횟수 추적
- 실패 원인 분류 (문법 오류, 잘못된 테이블명, 논리 오류 등)

### 4. 결과 리포트 생성
- `data/evaluation/sql_eval_results.json`에 저장
- 메트릭:
  - `execution_accuracy`: 실행 성공률
  - `result_accuracy`: 결과 정확도
  - `avg_retry_count`: 평균 재시도 횟수
  - `error_distribution`: 오류 유형별 분포

### 수용 기준
- Execution Accuracy 80% 이상
- Result Accuracy 75% 이상

**Test Strategy:**

## 검증 방법

1. **평가 스크립트 실행**
```bash
python scripts/evaluate_sql.py
```

2. **예상 출력**
```
SQL Agent Evaluation Results:
- Execution Accuracy: 85.0% (17/20 succeeded)
- Result Accuracy: 80.0% (16/20 correct)
- Avg Retry Count: 1.2
- Error Distribution:
  - Syntax Error: 2
  - Wrong Table: 1
  - Logic Error: 0

PASSED: Execution Accuracy >= 80%
```

3. **실패 케이스 수동 검증**
- 실패한 3개 질문에 대해 수동 SQL 작성
- 난이도가 너무 높은지 평가

4. **재시도 효과 분석**
- Self-Correction으로 성공한 케이스 식별
- 재시도 없이 성공률과 비교
