from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = "vectorstore/chroma_db"

# Load embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load vector database
vectordb = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embedding_model
)

# Test query
query = "What should I do if a circuit breaker overheats?"

results = vectordb.similarity_search(query, k=3)

print("\nTop Retrieved Chunks:\n")

for i, doc in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(doc.page_content[:1000])