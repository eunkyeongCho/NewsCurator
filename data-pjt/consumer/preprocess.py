from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 기자, 이메일 전처리
def splitfront(writer_string: str) -> str:
    """
    기자 이름 추출 (예: '홍길동 기자 hong@news.com' → '홍길동 기자')
    """
    if not writer_string:
        return None
    if "기자" in writer_string:
        return writer_string.split("기자")[0].strip() + " 기자"
    return writer_string.strip()

def splitback(writer_string: str) -> str:
    """
    이메일 추출 (예: '홍길동 기자 hong@news.com' → 'hong@news.com')
    """
    if not writer_string:
        return None
    if "기자" in writer_string:
        parts = writer_string.split("기자")
        if len(parts) > 1:
            email_candidate = parts[1].strip()
            if "@" in email_candidate:
                return email_candidate
    return None

def preprocess_content(content):
    """
    데이터 전처리 - 텍스트 길이 제한  (5000 토큰)
    토큰 수를 제한하여 처리 효율성 확보
    """
    import tiktoken

    if not content:
        return ""
        
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(content)
    
    if len(tokens) > 5000:
        truncated_tokens = tokens[:5000]
        return encoding.decode(truncated_tokens)
    
    return content


def transform_extract_keywords(text):
    text = preprocess_content(text)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "다음 뉴스 기사 본문에서 핵심 키워드 5개를 쉼표로 구분하여 추출해주세요."
            },
            {"role": "user", "content": text}
        ],
        max_tokens=100
    )
    keywords = response.choices[0].message.content.strip()
    return [k.strip() for k in keywords.split(",")]


def transform_to_embedding(text: str) -> bytes:
    """
    뉴스 본문을 1536차원 임베딩 벡터로 변환하고 바이너리로 반환
    """
    try:
        text = preprocess_content(text)
        print("[임베딩 시작] 텍스트 길이:", len(text))
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        embedding = response.data[0].embedding
        print("[임베딩 성공] 벡터 크기:", len(embedding))
        # 리스트를 바이너리로 변환
        binary_data = json.dumps(embedding).encode('utf-8')
        print("[변환 완료] 바이너리 크기:", len(binary_data))
        return binary_data
    except Exception as e:
        print(f"[임베딩 실패] 오류: {e}")
        return None


def transform_classify_category(content):
    text = preprocess_content(content)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "다음 뉴스 기사 본문을 읽고 가장 적절한 카테고리를 다음 목록 중에서 하나만 선택해서 출력하세요:\n"
                    "IT_과학, 건강, 경제, 교육, 국제, 라이프스타일, 문화, 사건사고, 사회일반, 산업, 스포츠, "
                    "여성복지, 여행레저, 연예, 정치, 지역, 취미"
                )
            },
            {"role": "user", "content": text}
        ],
        max_tokens=20,
        temperature=0.2
    )
    model_output = response.choices[0].message.content.strip()

    if model_output not in [
        "IT_과학", "건강", "경제", "교육", "국제", "라이프스타일", "문화", "사건사고",
        "사회일반", "산업", "스포츠", "여성복지", "여행레저", "연예", "정치", "지역", "취미"
    ]:
        model_output = "미분류"

    return model_output

