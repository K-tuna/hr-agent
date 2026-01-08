#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
글자 수 카운터
- 공백 포함
- 공백 미포함
- 특수문자 미포함 (순수 텍스트만)
"""

import sys
import re
import os


def count_characters(file_path: str) -> dict:
    """파일의 글자 수를 다양한 기준으로 계산"""
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. 공백 포함 (전체)
    total_with_spaces = len(content)
    
    # 2. 공백 미포함 (공백, 탭, 줄바꿈 제외)
    no_spaces = re.sub(r'\s', '', content)
    total_no_spaces = len(no_spaces)
    
    # 3. 특수문자 미포함 (한글, 영문, 숫자만)
    # Markdown 특수문자: |, -, #, *, _, `, [, ], (, ), etc.
    only_text = re.sub(r'[^\w가-힣a-zA-Z0-9]', '', content)
    total_only_text = len(only_text)
    
    # 4. 순수 한글만
    only_korean = re.sub(r'[^가-힣]', '', content)
    total_korean = len(only_korean)
    
    # 5. 줄 수
    lines = content.count('\n') + 1
    
    return {
        "with_spaces": total_with_spaces,
        "no_spaces": total_no_spaces,
        "only_text": total_only_text,
        "only_korean": total_korean,
        "lines": lines
    }


def format_number(n: int) -> str:
    """숫자에 천 단위 콤마 추가"""
    return f"{n:,}"


def print_result(file_path: str, counts: dict):
    """결과 출력"""
    filename = os.path.basename(file_path)
    
    print()
    print(f"[Result] {filename}")
    print("=" * 45)
    print(f"  With spaces:        {format_number(counts['with_spaces']):>12}")
    print(f"  No spaces:          {format_number(counts['no_spaces']):>12}")
    print(f"  Text only:          {format_number(counts['only_text']):>12}")
    print(f"  Korean only:        {format_number(counts['only_korean']):>12}")
    print("-" * 45)
    print(f"  Total lines:        {format_number(counts['lines']):>12}")
    print()
    
    # 비율 분석
    if counts['with_spaces'] > 0:
        space_ratio = (1 - counts['no_spaces'] / counts['with_spaces']) * 100
        special_ratio = (1 - counts['only_text'] / counts['no_spaces']) * 100 if counts['no_spaces'] > 0 else 0
        
        print("[Analysis]")
        print("-" * 45)
        print(f"  Space ratio:        {space_ratio:>11.1f}%")
        print(f"  Special char ratio: {special_ratio:>11.1f}%")
        print()


def main():
    # 기본 파일 경로 (인자 없으면 회사규정.txt)
    default_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "company_docs", "회사규정.txt"
    )
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = default_path
    
    # 파일 존재 확인
    if not os.path.exists(file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)
    
    # 글자 수 계산
    counts = count_characters(file_path)
    
    # 결과 출력
    print_result(file_path, counts)


if __name__ == "__main__":
    main()

