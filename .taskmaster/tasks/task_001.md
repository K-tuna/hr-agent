# Task ID: 1

**Title:** RAGAS 평가 프레임워크 구축

**Status:** pending

**Dependencies:** None

**Priority:** high

**Description:** RAG Agent의 품질을 측정하기 위한 RAGAS 평가 시스템 구현 (Faithfulness, Answer Relevancy, Context Precision)

**Details:**

## 구현 세부사항

### 1. RAGAS 설치 및 설정
- `pip install ragas==0.2.0` (최신 안정 버전)
- `langchain-openai` 통합 (기존 OpenAI 임베딩 재사용)

### 2. 평가 데이터셋 생성
- `data/evaluation/rag_eval_dataset.json` 파일 생성
- 최소 20개의 질문-답변-컨텍스트 쌍
- 예시 형식:
```json
{
  "question": "육아휴직은 몇 개월까지 가능해?",
  "answer": "육아휴직은 최대 1년(12개월)까지 가능합니다.",
  "contexts": ["관련 규정 텍스트"],
  "ground_truth": "1년(12개월)"
}
```

### 3. 평가 스크립트 작성
- `scripts/evaluate_rag.py` 생성
- RAGAS 메트릭 계산:
  - `faithfulness`: 답변이 컨텍스트에 충실한지
  - `answer_relevancy`: 답변이 질문에 관련있는지
  - `context_precision`: 검색된 컨텍스트의 정확도
- 종합 점수 계산 및 리포트 생성

### 4. 평가 결과 저장
- `data/evaluation/rag_eval_results.json`에 결과 저장
- 각 메트릭별 점수 및 실패 케이스 분석

### 5. CI/CD 통합 (선택)
- GitHub Actions에서 자동 평가 실행
- 품질 임계값 체크 (0.7 이상)

### 수용 기준
- RAGAS 종합 점수 0.7 이상 달성
- 20개 이상의 평가 데이터셋 구축
- 자동 평가 스크립트 실행 가능

**Test Strategy:**

## 검증 방법

1. **평가 스크립트 실행**
```bash
python scripts/evaluate_rag.py
```

2. **예상 출력**
```
RAGAS Evaluation Results:
- Faithfulness: 0.82
- Answer Relevancy: 0.78
- Context Precision: 0.85
- Overall Score: 0.82

PASSED: Score >= 0.7 threshold
```

3. **결과 파일 확인**
- `data/evaluation/rag_eval_results.json` 파일 존재
- 모든 메트릭 값이 0.0~1.0 범위 내

4. **실패 케이스 분석**
- 점수 0.5 미만인 질문 식별
- 개선 방향 문서화
