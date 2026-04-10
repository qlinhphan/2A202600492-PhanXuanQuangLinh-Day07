from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        # TODO: store references to store and llm_fn
        self.store = store
        self.llm_fn = llm_fn
        # pass

    def answer(self, question: str, top_k: int = 3) -> str:
        # TODO: retrieve chunks, build prompt, call llm_fn
        # 1. Tìm tài liệu liên quan
        results = self.store.search(question, top_k=top_k)
        
        # 2. Rút trích nội dung tìm được
        contexts = [res["content"] for res in results]
        context_text = "\n\n".join(contexts)
        
        # 3. Tạo Prompt
        prompt = f"""Dựa vào các thông tin sau: {context_text} Hãy trả lời câu hỏi: {question}"""

        # 4. Gọi LLM
        return self.llm_fn(prompt)
