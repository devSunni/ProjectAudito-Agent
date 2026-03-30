---
description: Project Refactor Pro - Universal Standard Workflow
---

# Project Refactor Pro: Standard Workflow

이 워크플로우는 프로젝트의 아키텍처 결함을 수정하고, 테스트 품질을 높이며, 유지보수가 용이한 구조로 전환하기 위한 에이전트의 표준 지침입니다.

## 1. 분석 단계 (Analysis)
- `Project Auditor Pro` (`auditor.py`)를 실행하여 현재 상태를 진단합니다.
- 다음 항목을 중점적으로 기술 부채로 식별합니다:
  - **테스트 갭**: 구현 코드는 있으나 대응하는 테스트 파일이 없는 경우.
  - **구조적 혼란**: 소스 코드와 자산(Assets), 대규모 데이터가 혼재된 경우.
  - **일관성 부재**: 명명 규칙(Naming Convention)이나 로깅 패턴이 파편화된 경우.

## 2. 설계 및 계획 단계 (Planning)
- 해당 언어/프레임워크의 Best Practice에 따른 디렉토리 구조를 제안합니다.
  - (예: Python/FastAPI -> `app/`, `core/`, `api/`, `models/`, `tests/`)
  - (예: React/Next.js -> `src/components/`, `src/hooks/`, `src/services/`, `__tests__/`)
- `implementation_plan.md`를 생성하여 다음 내용을 포함합니다:
  - 변경될 디렉토리 구조도 (Tree).
  - 이동/삭제될 파일 목록.
  - 주요 인터페이스 및 임포트 경로 변경 계획.

## 3. 실행 단계 (Execution)
// turbo
1. **환경 준비**: 필요한 디렉토리를 생성합니다 (`mkdir -p`).
2. **코드 이동**: 파일을 새로운 위치로 옮기고, 정적 분석 툴을 통해 임포트 깨짐을 수정합니다.
3. **테스트 보강**: `auditor --fix-tests`를 실행하여 누락된 테스트 스켈레톤을 자동으로 생성한 뒤 내용을 채웁니다.
4. **문서화**: `auditor --update-readme`를 실행하여 `README.md`에 변경된 프로젝트 구조를 자동으로 반영합니다.

## 4. 검증 단계 (Verification)
- 전체 테스트 스위트를 실행하여 회귀 오류(Regression)가 없는지 확인합니다.
- `auditor`를 재실행하여 리포트 상의 지표(Test Coverage)가 개선되었는지 확인합니다.
- `walkthrough.md`를 작성하여 사용자에게 변경 사항을 시각적으로 설명합니다.

---
> [!TIP]
> 이 가이드는 모든 프로젝트의 `.agents/workflows/` 폴더에 복사하여 즉시 활용할 수 있습니다.
