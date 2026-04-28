# Hierarchical Swarm / Virtual Company (대규모 계층형 군집 에이전트)

## 1. 프로젝트 개요

이 프로젝트는 단일 에이전트의 한계를 넘어, 조직의 계층 구조를 모방한 대규모 멀티 에이전트 시스템(MAS) 아키텍처를 구현합니다. 

상위 그래프의 프로덕트 매니저(PM)가 프로젝트의 전체 기획서(PRD)를 작성하면, 하위 그래프로 설계된 '개발 부서' 노드가 호출됩니다. 개발 부서 내부에는 프로그래머와 리뷰어가 상주하여 코드가 완성될 때까지 자체적인 루프를 돌며 품질을 보증합니다. 이러한 '그래프 안의 그래프(Graph-in-Graph)' 구조는 컨텍스트 병목을 해소하고 유지보수성을 높이는 엔터프라이즈급 설계 패턴입니다.

## 2. 시스템 아키텍처 및 워크플로우

본 시스템은 상위 지휘 계통과 하위 실무 부서로 나뉘어 동작합니다.

### 2.1 상위 그래프 (Virtual Company)
1. PM Node: 사용자의 목표를 분석하여 제품 요구사항 정의서(PRD)를 마크다운 형식으로 작성합니다.
2. Dev Department Node: 작성된 PRD를 하위 그래프에 전달하고 실무를 위임합니다. 하위 그래프의 최종 결과물만 수신하여 프로젝트를 마무리합니다.

### 2.2 하위 그래프 (Dev Department)
1. Programmer Node: 전달받은 PRD를 바탕으로 소스 코드를 작성합니다. 리뷰어의 피드백이 있을 경우 이를 반영하여 코드를 수정합니다.
2. Reviewer Node: 작성된 코드가 PRD의 모든 예외 조건과 기능 명세를 충족하는지 검토합니다. 승인 또는 반려 피드백을 산출합니다.

## 3. 기술 스택

* Language: Python 3.10+
* Package Manager: uv
* LLM: OpenAI gpt-5.4-nano (reasoning_effort="high" 설정을 통한 정밀 추론)
* Orchestration: LangGraph (계층형 그래프 및 상태 전이 제어), LangChain
* Data Validation: Pydantic (v2) (리뷰 결과 및 승인 여부 구조화)
* Web Framework: Streamlit (계층별 진행 상황 모니터링)

## 4. 프로젝트 구조
```
virtual-company/
├── .env                  
├── requirements.txt      
├── main.py               
└── app/
    ├── __init__.py
    └── graph.py          
```
## 5. 핵심 준수 사항 (개발 가이드라인)

시스템의 안정성과 확장성을 위해 다음 규칙을 엄격히 준수하여 개발되었습니다.

* 프롬프트 템플릿 보안: ChatPromptTemplate 구성 시 파이썬 f-string을 사용하지 않습니다. 이는 기획서나 코드 내에 포함될 수 있는 중괄호({})와 템플릿 변수가 충돌하여 발생하는 KeyError를 방지하기 위함입니다. 변수는 .invoke() 단계에서 딕셔너리로 주입합니다.
* 상태 참조 안정성: 초기화 지연으로 인한 오류를 방지하기 위해 state["key"] 방식 대신 반드시 state.get("key", 기본값) 메서드를 사용하여 상태를 참조합니다.
* 계층적 캡슐화: 하위 그래프는 자신의 독립된 상태(DevState)를 가지며, 상위 그래프는 하위 그래프의 내부 로직에 관여하지 않고 오직 입력과 출력 데이터로만 소통합니다.
* 스트리밍 예외 처리: app_graph.stream() 결과를 처리할 때, 특정 노드의 반환값이 None일 경우를 대비하여 반드시 Null Check 로직을 수행합니다.

## 6. 설치 및 실행 가이드

### 6.1 환경 변수 설정
프로젝트 루트 경로에 .env 파일을 생성하고 OpenAI API 키를 입력하십시오.
OPENAI_API_KEY=sk-your-api-key-here

### 6.2 의존성 설치 및 실행
uv venv
uv pip install -r requirements.txt
uv run streamlit run main.py

## 7. 테스트 시나리오 및 검증

1. 대규모 작업 발주: "사용자 인증, 비밀번호 암호화, DB 연결을 포함한 게시판 백엔드 모듈 개발"과 같은 복합적인 목표를 입력합니다.
2. PM 기획 확인: 상위 노드가 단순히 코드를 짜는 것이 아니라, 실무 부서에 넘길 수 있는 정교한 PRD 문서를 선제적으로 생성하는지 확인합니다.
3. 하위 루프 검증: 개발 부서 내부에서 프로그래머와 리뷰어가 서로 의견을 주고받으며 코드를 고도화하는 과정이 정상적으로 수행되는지 모니터링합니다.
4. 최종 결과물 수렴: 모든 내부 검증이 완료된 고품질의 코드가 상위 그래프로 최종 반환되어 출력되는지 점검합니다.

## 8. 실행 화면

<img width="1093" height="838" alt="스크린샷 2026-04-28 100407" src="https://github.com/user-attachments/assets/520527d7-9035-4ce0-8850-9b9839d35c50" />
<img width="1014" height="1220" alt="스크린샷 2026-04-28 100140" src="https://github.com/user-attachments/assets/0d60e451-a77a-46d9-8830-a956ffee2a47" />

