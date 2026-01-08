#!/usr/bin/env python3
"""
Ollama 모델 비교 스크립트
3개 로컬 LLM 모델의 성능을 비교합니다.

사용법:
    # 먼저 Ollama 모델 다운로드
    ollama pull llama3.1:8b
    ollama pull mistral:7b
    ollama pull qwen2.5:7b

    # 스크립트 실행
    python scripts/compare_models.py
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.llm.factory import create_chat_model


@dataclass
class ModelResult:
    """모델 테스트 결과"""
    model_name: str
    question: str
    answer: str
    latency_ms: float
    success: bool
    error: str = ""


# 비교할 모델 목록
MODELS_TO_COMPARE = [
    "qwen3:8b",       # Alibaba, 2025.04 출시, 한국어 최강, Qwen2.5-72B 수준 성능
    "llama3.1:8b",    # Meta, 가장 범용적, 안정적
    "mistral:7b",     # 프랑스 Mistral AI, 코드 생성에 강점
]

# 테스트 질문 (SQL 생성 능력 테스트)
SQL_TEST_QUESTIONS = [
    "직원 수는 몇 명인가요?",
    "개발팀 평균 급여를 조회하는 SQL을 작성해줘",
    "2024년에 입사한 직원 목록을 보여줘",
]

# 테스트 질문 (한국어 이해도 테스트)
KOREAN_TEST_QUESTIONS = [
    "연차휴가는 며칠인가요?",
    "육아휴직 기간에 대해 알려줘",
]


def test_model(model_name: str, questions: List[str]) -> List[ModelResult]:
    """
    단일 모델 테스트

    Args:
        model_name: Ollama 모델명
        questions: 테스트 질문 목록

    Returns:
        테스트 결과 목록
    """
    results = []

    try:
        llm = create_chat_model(
            provider="ollama",
            model=model_name,
            temperature=0,
            base_url="http://localhost:11434"
        )
    except Exception as e:
        print(f"[ERROR] {model_name} 로드 실패: {e}")
        return [
            ModelResult(
                model_name=model_name,
                question=q,
                answer="",
                latency_ms=0,
                success=False,
                error=str(e)
            )
            for q in questions
        ]

    for question in questions:
        start_time = time.time()
        try:
            response = llm.invoke(question)
            latency_ms = (time.time() - start_time) * 1000
            results.append(ModelResult(
                model_name=model_name,
                question=question,
                answer=response.content[:200] + "..." if len(response.content) > 200 else response.content,
                latency_ms=latency_ms,
                success=True
            ))
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            results.append(ModelResult(
                model_name=model_name,
                question=question,
                answer="",
                latency_ms=latency_ms,
                success=False,
                error=str(e)
            ))

    return results


def print_comparison_table(all_results: Dict[str, List[ModelResult]]):
    """비교 결과 테이블 출력"""
    print("\n" + "=" * 80)
    print("모델 비교 결과")
    print("=" * 80)

    # 모델별 평균 응답 시간
    print("\n## 평균 응답 시간 (ms)")
    print("-" * 40)
    for model_name, results in all_results.items():
        successful = [r for r in results if r.success]
        if successful:
            avg_latency = sum(r.latency_ms for r in successful) / len(successful)
            success_rate = len(successful) / len(results) * 100
            print(f"{model_name:20s}: {avg_latency:8.1f} ms (성공률: {success_rate:.0f}%)")
        else:
            print(f"{model_name:20s}: 실패")

    # 질문별 상세 결과
    print("\n## 질문별 상세 결과")
    print("-" * 80)

    questions = SQL_TEST_QUESTIONS + KOREAN_TEST_QUESTIONS
    for i, question in enumerate(questions):
        print(f"\n### Q{i+1}: {question}")
        print("-" * 60)
        for model_name, results in all_results.items():
            result = results[i] if i < len(results) else None
            if result and result.success:
                print(f"\n[{model_name}] ({result.latency_ms:.0f}ms)")
                print(f"  {result.answer}")
            elif result:
                print(f"\n[{model_name}] 실패: {result.error}")


def main():
    """메인 함수"""
    print("=" * 80)
    print("Ollama 모델 비교 스크립트")
    print("=" * 80)
    print(f"\n테스트 모델: {', '.join(MODELS_TO_COMPARE)}")
    print(f"테스트 질문 수: {len(SQL_TEST_QUESTIONS) + len(KOREAN_TEST_QUESTIONS)}")

    # Ollama 서버 확인
    print("\n[1/3] Ollama 서버 연결 확인...")
    try:
        test_llm = create_chat_model(
            provider="ollama",
            model="llama3.1:8b",
            base_url="http://localhost:11434"
        )
        print("  - Ollama 서버 연결 성공")
    except Exception as e:
        print(f"  - Ollama 서버 연결 실패: {e}")
        print("\n[TIP] Ollama가 실행 중인지 확인하세요:")
        print("  1. ollama serve (터미널에서)")
        print("  2. ollama pull llama3.1:8b")
        return

    # 모델 테스트
    print("\n[2/3] 모델 테스트 시작...")
    all_results = {}
    all_questions = SQL_TEST_QUESTIONS + KOREAN_TEST_QUESTIONS

    for model_name in MODELS_TO_COMPARE:
        print(f"\n  테스트 중: {model_name}")
        results = test_model(model_name, all_questions)
        all_results[model_name] = results
        successful = sum(1 for r in results if r.success)
        print(f"    - 완료: {successful}/{len(results)} 성공")

    # 결과 출력
    print("\n[3/3] 결과 분석...")
    print_comparison_table(all_results)

    # 추천 모델
    print("\n" + "=" * 80)
    print("## 추천 모델")
    print("-" * 40)

    # 가장 빠른 모델 찾기
    fastest_model = None
    fastest_latency = float('inf')
    for model_name, results in all_results.items():
        successful = [r for r in results if r.success]
        if successful:
            avg_latency = sum(r.latency_ms for r in successful) / len(successful)
            if avg_latency < fastest_latency:
                fastest_latency = avg_latency
                fastest_model = model_name

    if fastest_model:
        print(f"  - 가장 빠른 모델: {fastest_model} ({fastest_latency:.0f}ms)")
        print(f"  - 한국어 성능 권장: qwen3:8b (Qwen2.5-72B 수준, 119개 언어)")
        print(f"  - 코드 생성 권장: mistral:7b")
        print(f"  - 범용 권장: llama3.1:8b")

    print("\n" + "=" * 80)
    print("비교 완료!")


if __name__ == "__main__":
    main()
