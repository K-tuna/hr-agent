# SLM 전환 및 파인튜닝 PRD

## 개요
OpenAI API 의존성을 제거하고 로컬 SLM(Ollama + Qwen3)으로 전환하여 비용 절감, 보안 강화, 도메인 특화 성능 향상을 달성한다.

## 배경
- 현업에서 보안/규정 이슈로 외부 API 사용 제한
- API 비용 최적화 필요
- HR 도메인 특화 모델로 정확도 향상 가능

## 이미 완료된 작업
- core/llm/factory.py: LLM Factory 패턴 구현 (OpenAI/Ollama 스위칭)
- scripts/compare_models.py: 모델 비교 스크립트 작성

---

## 태스크 목록

### Task 1: Agent에 Ollama 연동
기존 Agent(SQL Agent, RAG Agent, Router)에서 OpenAI 하드코딩 부분을 LLM Factory로 교체.
- app/core/config.py에 LLM_PROVIDER, LLM_MODEL, OLLAMA_BASE_URL 환경변수 추가
- core/container.py에서 설정 기반 LLM 인스턴스 생성
- SQL Agent, RAG Agent, Router에서 factory 함수 사용하도록 수정
- .env.example 업데이트

### Task 2: Qwen3 vs GPT-4o-mini 벤치마크
동일한 테스트셋으로 두 모델 성능 비교.
- 테스트 데이터셋 구축 (SQL 20개, RAG 20개)
- 평가 메트릭: 정확도, 응답시간, 토큰 수
- scripts/benchmark_models.py 작성
- 결과 리포트 생성 (docs/benchmark/)

### Task 3: HR 파인튜닝 데이터셋 구축
Qwen3 파인튜닝을 위한 HR 도메인 데이터셋 생성.
- SQL 생성 데이터: 질문-SQL-결과 100개 쌍
- 규정 QA 데이터: 질문-답변-컨텍스트 100개 쌍
- 데이터 형식: Alpaca 또는 ShareGPT 포맷
- data/finetuning/ 디렉토리에 저장

### Task 4: Qwen3 파인튜닝 실행
HR 도메인 데이터로 Qwen3 LoRA 파인튜닝.
- Unsloth 또는 LLaMA-Factory 활용
- LoRA rank 8~16, epochs 3~5
- 파인튜닝 스크립트 작성 (scripts/finetune_qwen3.py)
- 체크포인트 저장 (models/qwen3-hr-finetuned/)

### Task 5: 파인튜닝 전후 성능 비교
Base Qwen3 vs Fine-tuned Qwen3 비교.
- 동일 테스트셋으로 평가
- 정확도 향상률 측정
- 포트폴리오용 Before/After 리포트 작성
- docs/finetuning-report.md 생성

---

## 성공 기준
- Ollama 연동: 환경변수만으로 OpenAI ↔ Ollama 전환 가능
- 벤치마크: Qwen3가 GPT-4o-mini 대비 90% 이상 성능
- 파인튜닝: Base 대비 10% 이상 정확도 향상
