from langchain_community.llms import Ollama
from django.core.cache import cache

def generate_email_response_function(prompt, regenerate=False):
    # llm = Ollama(model="llama3.1")
    llm = Ollama(model="llama3.2")
    # llm = Ollama(model="gemma2:9b")

    # Check if the response is already cached and regenerate is False
    if not regenerate:
        cached_response = cache.get('email_response_' + prompt )
        if cached_response:
            return cached_response
        
    text = """
            You are an intelligent assistant that helps users generate professional emails. 
            When a user provides basic information, you will craft a well-structured and properly formatted email based on the given context. 
            Ensure that the email follows standard business communication practices, including a formal or semi-formal greeting depending on the recipient’s relationship with the user. 
            Briefly state the purpose or context in the introduction, then address the main points clearly and concisely in the body of the email. 
            Conclude the email politely, offering next steps or expressing gratitude as needed. 
            Use an appropriate sign-off such as "Best regards" or "Sincerely" and, if requested, include the user’s name, title, and contact information. 
            The overall tone should match the user’s preference (formal, neutral, or casual), and the email should be clear, polite, and free of errors.
        """

    # Generate text based on the input prompt
    response = llm(prompt+text)
    generated_text = response

    # Cache the response for a certain amount of time (e.g., 1 hour)
    cache.set('email_response_' + prompt, generated_text, 3600)
    print(generated_text)
    return generated_text