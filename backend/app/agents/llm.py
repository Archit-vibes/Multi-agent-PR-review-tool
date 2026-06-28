from langchain_litellm import ChatLiteLLM

def get_llm():
    """
    Returns a ChatLiteLLM instance with Groq as primary and Gemini as fallback.
    """
    # Primary Model (Groq)
    primary_llm = ChatLiteLLM(
        model="groq/llama-3.3-70b-versatile",
        temperature=0.2
    )
    
    # Fallback Model (Gemini)
    fallback_llm = ChatLiteLLM(
        model="gemini/gemini-2.5-flash",
        temperature=0.2
    )
    
    # Langchain fallback routing
    return primary_llm.with_fallbacks([fallback_llm])
