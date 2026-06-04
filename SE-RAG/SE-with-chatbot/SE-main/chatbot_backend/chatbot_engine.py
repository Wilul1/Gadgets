import os
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv

# Import our custom modules
from intent_router import route_intent
from firebase_connector import get_iphone_inventory, get_order_status

load_dotenv()

# Check for API key
if not os.environ.get("GROQ_API_KEY"):
    print("WARNING: GROQ_API_KEY is not set. Please set it in your environment or a .env file.")

client = Groq()

def analyze_sentiment(user_input):
    """
    Quick LLM call to analyze sentiment to manage frustration.
    Returns 'frustrated' or 'neutral'.
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a sentiment analyzer. Output only the word 'frustrated' if the user sounds angry, annoyed, or frustrated. Otherwise, output 'neutral'."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.0,
            max_tokens=10
        )
        sentiment = completion.choices[0].message.content.strip().lower()
        if "frustrated" in sentiment:
            return "frustrated"
        return "neutral"
    except Exception as e:
        return "neutral"

# Global initialization for ChromaDB and Embeddings
_chroma_client = None
_sentence_transformer_ef = None

def _get_chroma_setup():
    global _chroma_client, _sentence_transformer_ef
    persist_directory = "./chroma_db"
    if not os.path.exists(persist_directory):
        return None, None
        
    if _chroma_client is None:
        try:
            _chroma_client = chromadb.PersistentClient(path=persist_directory)
            _sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        except Exception:
            return None, None
    return _chroma_client, _sentence_transformer_ef

def retrieve_faq_context(query):
    """
    Queries ChromaDB for relevant FAQ context.
    """
    client, ef = _get_chroma_setup()
    if not client or not ef:
        return "No FAQ database found or failed to load."
        
    try:
        collection = client.get_collection(name="cho_wy_faqs", embedding_function=ef)
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        if results['documents'] and results['documents'][0]:
            return " ".join(results['documents'][0])
        return "No relevant FAQ found."
    except Exception as e:
        return f"Error retrieving FAQ: {e}"

def generate_response(user_input, conversation_history, is_first_message):
    intent = route_intent(user_input)
    sentiment = analyze_sentiment(user_input)
    
    formatted_context = ""
    if intent == "faq":
        formatted_context = retrieve_faq_context(user_input)
    elif intent == "inventory":
        formatted_context = get_iphone_inventory()
    elif intent == "order_status":
        formatted_context = get_order_status(user_input)

    system_prompt = f"""
You are the official customer support AI for Cho Wy Gadgets.
Store Constraint: Cho Wy Gadgets EXCLUSIVELY SELLS Apple iPhones. We do NOT sell Samsung, Google Pixel, laptops, consoles, or any other brands.

The customer's current sentiment is: {sentiment}. If they are frustrated, be extra apologetic and empathetic.

CRITICAL INSTRUCTIONS (MUST OBEY):
1. DYNAMIC LANGUAGE MIRRORING: You MUST reply in the EXACT SAME LANGUAGE as the user's most recent message.
   - If user types English -> Reply 100% in English (e.g. "Our bestsellers are...").
   - If user types Tagalog -> Reply 100% in Tagalog.
   - If user types Taglish -> Reply in Taglish.
   Do not reply in Tagalog if the user speaks English!

2. OUT OF SCOPE PROTOCOL: If the user asks about anything unrelated to Cho Wy Gadgets (e.g., world politics, general knowledge, math, other industries), strictly decline. State you are an automated assistant exclusively for Cho Wy Gadgets.

3. IN SCOPE: Inquiries about what we sell (e.g., "What do you sell other than iPhones?", "What are your bestsellers?") are IN SCOPE. Answer by stating we only specialize in iPhones and pivot back to our available iPhone stock. NEVER invent fake products like Samsung or PS5.

Use the following context/inventory to answer the user's query:
{formatted_context}
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_input})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2
        )
        reply = completion.choices[0].message.content.strip()
        
        # Append to history for memory
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": reply})
        
        return reply, conversation_history
    except Exception as e:
        return f"Error communicating with LLM: {e}", conversation_history

def start_chat():
    print("Welcome to Cho Wy Gadgets Chatbot Testing Terminal!")
    print("Type 'exit' or 'quit' to stop.")
    print("-" * 50)
    
    conversation_history = []
    is_first_message = True
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        print("Bot is thinking...")
        response, conversation_history = generate_response(user_input, conversation_history, is_first_message)
        print(f"Cho Wy Bot: {response}")
        print("-" * 50)
        
        is_first_message = False

if __name__ == "__main__":
    start_chat()
