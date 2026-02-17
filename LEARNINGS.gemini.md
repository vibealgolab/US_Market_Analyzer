# LEARNINGS.gemini.md

## 📅 Date: 2026-02-17

## 🛠 Task: ag-kit init 명령어 실행 및 프로젝트 초기화

### 1. 발견된 문제 (Issue)
- 사용자가 `ag-kit init` 명령어를 요청했으나, 시스템 `PATH` 및 프로젝트 내에서 해당 이름의 실행 파일을 직접 찾을 수 없었음.
- 환경 변수 `ANTIGRAVITY_CLI_ALIAS=agy`가 설정되어 있었으나 `agy` 명령어도 즉시 등록되어 있지 않았음.

### 2. 해결 과정 (Solution)
- 시스템 환경 분석을 통해 도구 설치 경로인 `d:\z_Utilityprogram\Antigravity`를 발견함.
- `bin/antigravity.cmd` 파일이 실제 CLI 진입점임을 확인하고, 이를 통해 `init` 인자를 전달하여 실행함.
- 실행 결과, `web/` 폴더(Next.js)와 `AGENT_FLOW.md`를 포함한 'Antigravity Kit' 표준 아키텍처 파일들이 성공적으로 생성됨을 검증함.

### 3. 학습한 내용 (Learnings)
- **도구 식별**: `ag-kit`은 사용자가 설정한 별칭(Alias)이거나 Antigravity 에이전트 키트의 통칭이며, 실제 실행은 `antigravity.cmd`를 통해 이루어짐.
- **아키텍처 이해**: Antigravity Kit은 단순한 코드 모음이 아니라, Next.js 대시보드와 에이전트 워크플로우가 결합된 통합 개발 환경을 지향함.
- **환경 변수 활용**: `ANTIGRAVITY_AGENT` 및 `ANTIGRAVITY_CLI_ALIAS`와 같은 환경 변수가 에이전트 식별 및 도구 연결에 핵심적인 역할을 함.

### 4. 향후 권장 사항
- `d:\z_Utilityprogram\Antigravity\bin` 경로를 시스템 `PATH`에 추가하여 `antigravity` 또는 `ag-kit` 명령어를 어디서든 직접 호출할 수 있도록 설정할 것을 권장함.
