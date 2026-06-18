import os
import json
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load structural variables from .env file
load_dotenv()

class GeopoliticalVectorStore:
    def __init__(self):
        """Initializes the persistent storage layout and embedding models."""
        self.db_path = os.getenv("CHROMA_DB_PATH", "./vector_store")
        
        # 1. Initialize local persistent SQLite database client for Chroma
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # 2. Define the Embedding Function (Converts human text into vector coordinates)
        # We use an open-source, lightweight sentence-transformer model running locally
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # 3. Fetch or construct our collection inside the vector store
        self.collection = self.client.get_or_create_collection(
            name="geopolitical_knowledge_base",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"} # Using Cosine similarity metrics
        )

    def seed_database_from_json(self, json_file_path: str):
        """Reads raw historical data, extracts parameters, and indexes vectors."""
        path = Path(json_file_path)
        if not path.exists():
            print(f"❌ Error: Targets data source path not found at {json_file_path}")
            return
            
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
        print(f"🔄 Processing and indexing {len(data)} historical crisis profiles...")
        
        for item in data:
            # Upsert document vectors into the store safely
            self.collection.upsert(
                ids=[item["crisis_id"]],
                documents=[item["context"]],
                metadatas=[{
                    "event_name": item["event"],
                    "category": item["metadata"]["category"],
                    "primary_commodity": item["metadata"]["primary_commodity"],
                    "macro_regime": item["metadata"]["macro_regime"]
                }]
            )
        print("✅ Database seeding successfully finalized without errors.")

    def query_historical_context(self, current_headline: str, max_results: int = 1) -> list:
        """Performs a semantic similarity search against the historical archives."""
        results = self.collection.query(
            query_texts=[current_headline],
            n_results=max_results
        )
        
        extracted_contexts = []
        if results and results["documents"] and len(results["documents"][0]) > 0:
            for idx in range(len(results["documents"][0])):
                doc = results["documents"][0][idx]
                meta = results["metadatas"][0][idx]
                extracted_contexts.append({
                    "text": doc,
                    "associated_event": meta.get("event_name"),
                    "regime_impact": meta.get("macro_regime")
                })
        return extracted_contexts

# Verification execution pipeline block
if __name__ == "__main__":
    print("🚀 Initializing standalone validation sequence for GeopoliticalVectorStore...")
    
    # Instantiate the engine
    engine = GeopoliticalVectorStore()
    
    # Construct path routing and run seed verification
    base_dir = Path(__file__).resolve().parent.parent
    data_source = os.path.join(base_dir, "data", "raw_history.json")
    engine.seed_database_from_json(data_source)
    
    # Run a mock semantic retrieval check
    mock_signal = "Military escalations and drone actions targeting naval assets in maritime straits."
    print(f"\n🔍 Testing Semantic Vector Query: '{mock_signal}'")
    matches = engine.query_historical_context(mock_signal, max_results=1)
    
    if matches:
        print("\n🏆 Top Semantic Historical Match Retrieved:")
        print(f"🔹 Event: {matches[0]['associated_event']}")
        print(f"🔹 Regime Impact classification: {matches[0]['regime_impact']}")
        print(f"🔹 Context Excerpt: {matches[0]['text'][:150]}...")
    else:
        print("❌ Search verification yielded zero results. Review embedding parameters.")