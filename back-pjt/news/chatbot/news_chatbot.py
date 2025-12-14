from dotenv import load_dotenv
import os
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

# 이전 대화들 직렬화. 저장할 때 사용
def message_to_dict(msg):
    if isinstance(msg, SystemMessage):
        return {"type": "system", "content": msg.content}
    elif isinstance(msg, HumanMessage):
        return {"type": "human", "content": msg.content}
    elif isinstance(msg, AIMessage):
        return {"type": "ai", "content": msg.content}
    else:
        raise ValueError("Unknown message type")


# 이전 대화들 역직렬화. 불러들일 때 사용
def message_from_dict(d):
    if d["type"] == "system":
        return SystemMessage(content=d["content"])
    elif d["type"] == "human":
        return HumanMessage(content=d["content"])
    elif d["type"] == "ai":
        return AIMessage(content=d["content"])
    else:
        raise ValueError("Unknown message type")



def get_newsbot_response(messages, title, write_date, content, question):
    """
    messages: 이전 대화 메시지 리스트 (SystemMessage, HumanMessage, AIMessage)
    title, write_date, content: 기사 정보
    question: 사용자의 질문
    """
    # 첫 대화라면 system 프롬프트 추가
    if not messages:
        prompt = (
            f"너는 친절한 뉴스 비서 <뉴비>야.\n"
            f"- 뉴스 기사 내용을 바탕으로 사용자의 질문에 쉽고 친절하게 대답해줘.\n"
            f"- 기사의 내용에 없는 정보는 \"죄송해요, 여기 보고계신 기사에서는 찾을 수 없네요.\"라고 말해줘.\n\n"
            f"### 제목: {title}\n"
            f"### 작성일: {write_date}\n"
            f"### 내용: {content}\n"
        )
        messages = [SystemMessage(content=prompt)]
    # 질문 추가
    messages.append(HumanMessage(content=question))
    # LLM 호출
    llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")
    answer = llm.invoke(messages)
    # 답변 추가
    messages.append(AIMessage(content=answer.content))
    # 최근 20개만 유지
    messages = messages[-20:]
    return answer.content, messages