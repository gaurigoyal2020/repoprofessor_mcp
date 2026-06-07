from groq import Groq
from src.config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)


def call_llm(system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
    """
    Send a prompt to Groq and get a response back.
    
    system_prompt: sets the LLM's role and behaviour
    user_message: the actual question + retrieved code context
    max_tokens: max length of response (1024 ~ 750 words)
    """
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"LLM error: {str(e)}"


def build_context_from_chunks(chunks: list[dict]) -> str:
    """
    Format retrieved ChromaDB chunks into readable context for the LLM.
    
    Why format it this way? The LLM performs better when it can clearly 
    see which file each chunk came from. File path gives architectural 
    context — knowing code is in 'src/store/store.py' tells the LLM 
    it's a data layer concern.
    """
    if not chunks:
        return "No relevant code found in the repository."

    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"--- {chunk['path']} ---\n{chunk['content']}"
        )

    return "\n\n".join(context_parts)