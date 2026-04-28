import streamlit as st
from app.graph import app_graph

st.set_page_config(page_title="계층형 군집 에이전트", layout="wide")

st.title("대규모 계층형 군집 에이전트 (Hierarchical Swarm)")
st.markdown("하나의 상위 그래프가 복잡한 업무를 기획한 뒤, 자체적인 검증 루프를 가진 하위 그래프(Sub-graph)를 호출하여 실무를 위임하는 기업형 계층 아키텍처입니다.")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("프로젝트 발주")
    
    with st.form(key="project_form"):
        goal_input = st.text_area(
            "달성하고자 하는 프로젝트 목표를 입력하십시오.",
            placeholder="예: 사용자 로그인을 처리하고 JWT 토큰을 발급하는 안전한 파이썬 FastAPI 백엔드 구축",
            height=150
        )
        submit_btn = st.form_submit_button("프로젝트 가동", use_container_width=True)

with col2:
    st.subheader("실시간 프로젝트 진행 상황")

    if submit_btn and goal_input.strip():
        initial_state = {
            "project_goal": goal_input,
            "prd": "",
            "final_product": ""
        }

        final_result = ""

        with st.container(border=True, height=500):
            with st.spinner("가상 회사의 각 부서가 업무를 수행 중입니다..."):
                # 상위 그래프 스트리밍
                for output in app_graph.stream(initial_state):
                    # 방어 로직 필수 준수
                    if not output:
                        continue

                    for node_name, state_update in output.items():
                        if not state_update:
                            continue

                        if node_name == "pm":
                            st.info("[PM 부서] 제품 요구사항 정의서(PRD) 작성 완료.")
                            with st.expander("작성된 PRD 문서 확인"):
                                st.write(state_update.get("prd", ""))
                                
                        elif node_name == "dev_department":
                            st.success("[개발 부서] 내부 검토 루프 종료 및 최종 코드 납품 완료.")
                            final_result = state_update.get("final_product", "")

        st.subheader("최종 산출물 (코드)")
        if final_result:
            st.code(final_result, language="python")

    elif not submit_btn:
        st.info("좌측에 프로젝트 목표를 입력하고 작업을 시작하십시오.")