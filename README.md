# Project Auditor Pro 🚀

프로젝트의 아키텍처를 진단하고 테스트 커버리지 갭을 식별하며, 표준 리팩토링 워크플로우를 제공하는 범용 에이전트 도구입니다.

## 주요 기능

- **범용 언어 지원**: Python, JavaScript, TypeScript, Go, Rust 등 다양한 언어의 소스 및 테스트 구조를 인식합니다.
- **테스트 갭 분석**: 구현 파일에 대응하는 테스트 파일이 누락된 항목을 자동으로 찾아줍니다.
- **설정 가능**: `.auditor.json` 파일을 통해 프로젝트별 확장자, 제외 경로, 테스트 패턴을 커스터마이징할 수 있습니다.
- **표준 워크플로우**: 모든 프로젝트에 복사하여 바로 사용할 수 있는 `standard_refactor_guide.md`를 포함합니다.
- **마크다운 리포트**: 분석 결과를 시각적인 `audit_report.md`로 생성합니다.

## 설치 및 요구사항

- Python 3.8 이상
- 특별한 외부 의존성 없음 (표준 라이브러리만 사용)

## 사용 방법

### 1. 기본 분석 실행
프로젝트 루트에서 다음 명령을 실행합니다:
```bash
py auditor.py
```
*(Windows에서는 `py`를, 다른 OS에서는 `python3`를 사용하세요.)*

### 2. 특정 디렉토리 분석
```bash
py auditor.py --root ../another-project
```

### 3. 설정 파일 (.auditor.json)
프로젝트 루트에 설정 파일을 두어 동작을 제어할 수 있습니다.
```json
{
  "extensions": [".py", ".js", ".ts", ".jsx", ".tsx"],
  "source_dirs": ["src", "app"],
  "test_dirs": ["tests", "__tests__"],
  "test_prefix": "test_",
  "test_suffixes": ["_test", ".test", ".spec"]
}
```

## 구성 파일

- `auditor.py`: 메인 분석 스크립트.
- `standard_refactor_guide.md`: 프로젝트 구조 개선을 위한 가이드라인.
- `.auditor.json`: 기본 설정 파일.
- `tests/`: `Project Auditor Pro` 자체의 안정성을 검증하는 유닛 테스트.

---
*Created with ❤️ by devSunni*
