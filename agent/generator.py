import vertexai
from typing import List
from agent.retriever import retrieve
from config.config import Config
from vertexai.generative_models import GenerativeModel

vertexai.init(
    project=Config.PROJECT_ID,
    location=Config.LOCATION,
    credentials=Config.get_credentials(),
)
model = GenerativeModel(model_name=Config.MODEL_NAME)


def generate_answer(query: str, top_k: int = 5) -> str:
    docs = retrieve(query, top_k=top_k)
    context_text = "\n\n".join(docs["content"].tolist())
    print(context_text)
    prompt = f"""
    You are a helpful assistant that can answer questions and help with tasks.
    document context:
    {context_text}
    question:
    {query}
    Answer the question based on the document context.
    """
    response = model.generate_content(prompt)
    return response.text


if __name__ == "__main__":
    query = "什麼是 Python Decorator?"
    answer = generate_answer(query)
    print("Q:", query)
    print("A:", answer)
