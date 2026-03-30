# Project Auditor Pro 🚀

프로젝트의 아키텍처를 진단하고 테스트 커버리지 갭을 식별하며, 표준 리팩토링 워크플로우를 제공하는 범용 에이전트 도구입니다.

## 주요 기능

- **범용 언어 지원**: Python, JavaScript, TypeScript, Go, Rust 등 다양한 언어 인식.
- **테스트 갭 분석**: 구현 파일에 대응하는 테스트 파일 누락 항목 자동 식별.
- **GitIgnore 존중**: 대상 프로젝트의 `.gitignore` 설정을 자동으로 읽어 분석 대상에서 제외합니다.
- **Auto-Fixer (NEW)**: 누락된 유닛 테스트 스켈레톤을 생성하고, README의 프로젝트 구조 섹션을 자동으로 업데이트합니다.
- **설정 가능**: `.auditor.json` 파일을 통한 커스터마이징.

## 프로젝트 구조 (Auto-Updated) 📂

<!-- AUDITOR_STRUCTURE_START -->
```text
ProjectAudito-Agent
├── tests
│   └── test_auditor.py
├── .auditor.json
├── .gitignore
├── README.md
├── auditor.py
├── pyproject.toml
└── standard_refactor_guide.md
```
<!-- AUDITOR_STRUCTURE_END -->

## 설치 및 요구사항

### 1. 에이전트 모드로 설치 (전역 사용)
프로젝트 루트에서 다음 명령을 실행하여 현재 도구를 시스템에 등록합니다.
```bash
py -m pip install -e .
```

## 사용 방법

### 1. 전역 명령어 사용
어떤 프로젝트 폴더에서든 다음 명령을 실행하세요.
```bash
auditor
```
*(Windows PATH 문제로 `auditor`가 실행되지 않을 경우 `py -m auditor`를 사용하세요.)*

### 2. 특정 디렉토리 분석
```bash
auditor --root ../another-project
```

### 3. 설정 파일 (.auditor.json)
```json
{
  "extensions": [".py", ".js"],
  "exclude_dirs": ["node_modules", ".venv"]
}
```

## 개발 및 테스트

- `py tests/test_auditor.py`: 에이전트 자체 로직 검증.
- `py -m auditor --root .`: 현재 프로젝트 셀프 진단.

---
*Created with ❤️ by devSunni*
