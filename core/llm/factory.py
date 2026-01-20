"""
LLM Factory Module
Provider(openai/ollama)에 따라 적절한 LLM 인스턴스를 생성합니다.

사용법:
    from core.llm.factory import create_chat_model, create_embeddings

    # OpenAI 사용
    llm = create_chat_model(provider="openai", model="gpt-4o-mini")

    # Ollama 사용
    llm = create_chat_model(
        provider="ollama",
        model="llama3.1:8b",
        base_url="http://localhost:11434"
    )
"""

from typing import Optional, Union
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings


def create_chat_model(
    provider: str,
    model: str,
    temperature: float = 0,
    base_url: Optional[str] = None
) -> BaseChatModel:
    """
    Chat 모델 인스턴스 생성

    Args:
        provider: "openai" 또는 "ollama"
        model: 모델명 (예: "gpt-4o-mini", "llama3.1:8b")
        temperature: 응답 다양성 (0=결정적, 1=창의적)
        base_url: Ollama 서버 URL (ollama일 때만 사용)

    Returns:
        LangChain ChatModel 인스턴스

    Raises:
        ValueError: 지원하지 않는 provider일 경우

    Examples:
        >>> llm = create_chat_model("openai", "gpt-4o-mini")
        >>> llm = create_chat_model("ollama", "llama3.1:8b", base_url="http://localhost:11434")
    """
    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model,
            base_url=base_url or "http://localhost:11434",
            temperature=temperature
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, temperature=temperature)
    else:
        raise ValueError(f"지원하지 않는 LLM provider입니다: {provider}. 'openai' 또는 'ollama'를 사용하세요.")


def create_embeddings(
    provider: str,
    model: str,
    base_url: Optional[str] = None
) -> Embeddings:
    """
    Embedding 모델 인스턴스 생성 (RAG 벡터 검색용)

    Args:
        provider: "openai", "ollama", "google", 또는 "huggingface"
        model: 임베딩 모델명 (예: "text-embedding-3-small", "nomic-embed-text", "models/embedding-001", "intfloat/multilingual-e5-large-instruct")
        base_url: Ollama 서버 URL (ollama일 때만 사용)

    Returns:
        LangChain Embeddings 인스턴스

    Raises:
        ValueError: 지원하지 않는 provider일 경우

    Examples:
        >>> embeddings = create_embeddings("openai", "text-embedding-3-small")
        >>> embeddings = create_embeddings("ollama", "nomic-embed-text")
        >>> embeddings = create_embeddings("google", "models/embedding-001")
        >>> embeddings = create_embeddings("huggingface", "intfloat/multilingual-e5-large-instruct")
    """
    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(
            model=model,
            base_url=base_url or "http://localhost:11434"
        )
    elif provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=model)
    elif provider == "google":
        import os
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    elif provider == "huggingface":
        from sentence_transformers import SentenceTransformer

        class SentenceTransformerEmbeddings(Embeddings):
            def __init__(self, model_name: str):
                self.model = SentenceTransformer(model_name)

            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                return self.model.encode(texts, convert_to_numpy=True).tolist()

            def embed_query(self, text: str) -> list[float]:
                return self.model.encode(text, convert_to_numpy=True).tolist()

        return SentenceTransformerEmbeddings(model)
    else:
        raise ValueError(f"지원하지 않는 Embedding provider입니다: {provider}. 'openai', 'ollama', 'google', 또는 'huggingface'를 사용하세요.")
