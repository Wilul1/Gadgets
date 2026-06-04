import os
import chromadb
from docx import Document
from chromadb.utils import embedding_functions

def ingest_faqs(docx_path="Temporary/questions.docx", persist_directory="./chroma_db"):
    print(f"Loading document from {docx_path}...")
    try:
        doc = Document(docx_path)
    except Exception as e:
        print(f"Error loading {docx_path}: {e}")
        return

    # Extract text and split by paragraphs (we'll treat each non-empty paragraph as a chunk for simplicity, 
    # but ideally Q&A pairs are parsed. Adjust logic if Q&A pairs have specific formatting).
    chunks = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            chunks.append(text)

    if not chunks:
        print("No text found in document.")
        return

    print(f"Extracted {len(chunks)} chunks from the document.")

    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Use sentence-transformers
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="cho_wy_faqs",
        embedding_function=sentence_transformer_ef
    )
    
    # Add chunks
    print("Ingesting chunks into ChromaDB...")
    # Prepare ids
    ids = [f"faq_chunk_{i}" for i in range(len(chunks))]
    
    collection.upsert(
        documents=chunks,
        ids=ids
    )
    print("Successfully ingested FAQs into ChromaDB!")

if __name__ == "__main__":
    ingest_faqs()
