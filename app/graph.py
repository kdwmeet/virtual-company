from typing import TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ==========================================
# [하위 그래프] 개발 부서 (Dev Department) 정의
# ==========================================

class DevState(TypedDict):
    prd: str
    code: str
    review_feedback: str
    is_approved: bool

class ReviewResult(BaseModel):
    is_approved: bool = Field(description="코드가 기획서 요구사항을 완벽히 충족하면 true, 수정이 필요하면 false")
    feedback: str = Field(description="수정이 필요한 경우 구체적인 피드백 및 지시사항")

def programmer_node(state: DevState):
    """기획서(PRD)와 리뷰 피드백을 바탕으로 코드를 작성합니다."""
    # 심도 있는 코드 작성을 위해 reasoning_effort="high" 적용
    llm = ChatOpenAI(model="gpt-5.4-nano", reasoning_effort="high")
    
    prd = state.get("prd", "")
    feedback = state.get("review_feedback", "")

    if feedback:
        system_msg = "당신은 수석 프로그래머입니다. QA 부서의 피드백을 반영하여 기존 코드를 완벽하게 수정하십시오."
        user_msg = "기획서:\n{prd}\n\n이전 피드백:\n{feedback}\n\n수정된 코드를 작성하십시오."
        invoke_args = {"prd": prd, "feedback": feedback}
    else:
        system_msg = "당신은 수석 프로그래머입니다. 주어진 기획서(PRD)를 바탕으로 완벽한 코드를 작성하십시오."
        user_msg = "기획서:\n{prd}"
        invoke_args = {"prd": prd}

    # f-string 배제 및 딕셔너리 주입 원칙 준수
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("user", user_msg)
    ])

    response = (prompt | llm).invoke(invoke_args)
    return {"code": response.content}

def reviewer_node(state: DevState):
    """작성된 코드가 기획서(PRD)에 부합하는지 깐깐하게 검토합니다."""
    llm = ChatOpenAI(model="gpt-5.4-nano", reasoning_effort="high")
    structured_llm = llm.with_structured_output(ReviewResult)

    prd = state.get("prd", "")
    code = state.get("code", "")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 깐깐한 코드 리뷰어입니다. 작성된 코드가 기획서(PRD)의 요구사항을 예외 처리와 함께 모두 충족하는지 검토하십시오."),
        ("user", "기획서:\n{prd}\n\n작성된 코드:\n{code}")
    ])

    result: ReviewResult = (prompt | structured_llm).invoke({"prd": prd, "code": code})
    return {"is_approved": result.is_approved, "review_feedback": result.feedback}

def dev_router(state: DevState):
    """승인 여부에 따라 개발 루프를 순환하거나 종료합니다."""
    is_approved = state.get("is_approved", False)
    if is_approved:
        return END
    else:
        return "programmer"

# 하위 그래프 조립 및 컴파일
dev_workflow = StateGraph(DevState)
dev_workflow.add_node("programmer", programmer_node)
dev_workflow.add_node("reviewer", reviewer_node)
dev_workflow.add_edge(START, "programmer")
dev_workflow.add_edge("programmer", "reviewer")
dev_workflow.add_conditional_edges("reviewer", dev_router, {"programmer": "programmer", END: END})
dev_app = dev_workflow.compile()


# ==========================================
# [상위 그래프] 회사 전체 (Virtual Company) 정의
# ==========================================

class CompanyState(TypedDict):
    project_goal: str
    prd: str
    final_product: str

def pm_node(state: CompanyState):
    """전체 프로젝트 목표를 분석하여 상세한 제품 요구사항 정의서(PRD)를 작성합니다."""
    llm = ChatOpenAI(model="gpt-5.4-nano", reasoning_effort="high")
    goal = state.get("project_goal", "")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 뛰어난 프로덕트 매니저(PM)입니다. 주어진 프로젝트 목표를 달성하기 위한 구체적인 기능 명세와 예외 처리 조건이 포함된 제품 요구사항 정의서(PRD)를 마크다운으로 작성하십시오."),
        ("user", "프로젝트 목표: {goal}")
    ])

    response = (prompt | llm).invoke({"goal": goal})
    return {"prd": response.content}

def dev_department_node(state: CompanyState):
    """
    하위 그래프(dev_app)를 호출하여 개발 업무를 위임합니다.
    이 노드는 개발 부서 전체의 역할을 추상화합니다.
    """
    prd = state.get("prd", "")
    
    # 하위 그래프를 위한 초기 상태 설정
    initial_dev_state = {
        "prd": prd,
        "code": "",
        "review_feedback": "",
        "is_approved": False
    }

    # 하위 그래프 실행 (동기식 invoke 사용)
    dev_result = dev_app.invoke(initial_dev_state)

    # 하위 그래프의 최종 결과를 상위 그래프 상태로 반환
    final_code = dev_result.get("code", "")
    return {"final_product": final_code}

# 상위 그래프 조립 및 컴파일
company_workflow = StateGraph(CompanyState)
company_workflow.add_node("pm", pm_node)
company_workflow.add_node("dev_department", dev_department_node)

company_workflow.add_edge(START, "pm")
company_workflow.add_edge("pm", "dev_department")
company_workflow.add_edge("dev_department", END)

app_graph = company_workflow.compile()