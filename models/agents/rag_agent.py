import os
import pandas as pd
import logging
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

logger = logging.getLogger(__name__)

class RAGAgent:
    def __init__(self, llm):
        """Initialize the RAG agent with the provided LLM."""
        self.llm = llm
        
        try:
            # Initialize ChromaDB with product data
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.db = self._initialize_vector_store()
            
            # Setup RAG chain
            self.rag_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.db.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            logger.info("RAG Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Agent: {e}")
            self.rag_chain = None

    def _initialize_vector_store(self) -> Chroma:
        """Initialize the vector store with product and service data."""
        try:
            # Check if ChromaDB already exists
            persist_directory = "chroma_db"
            
            if os.path.exists(persist_directory):
                db = Chroma(persist_directory=persist_directory, embedding_function=self.embeddings)
                logger.info("Loaded existing ChromaDB")
                return db
            
            # Load and process CSV data
            documents = []
            
            # Load products data
            if os.path.exists("products_rag.csv"):
                products_df = pd.read_csv("products_rag.csv")
                for _, row in products_df.iterrows():
                    content = f"Product: {row.get('name', '')} - {row.get('description', '')} - Price: {row.get('price', 'N/A')}"
                    documents.append(Document(page_content=content, metadata={"type": "product", "source": "products_rag.csv"}))
            
            # Load services data
            if os.path.exists("services_rag.csv"):
                services_df = pd.read_csv("services_rag.csv")
                for _, row in services_df.iterrows():
                    content = f"Service: {row.get('name', '')} - {row.get('description', '')} - Price: {row.get('price', 'N/A')}"
                    documents.append(Document(page_content=content, metadata={"type": "service", "source": "services_rag.csv"}))
            
            if not documents:
                # Create some sample documents if no CSV files found
                documents = [
                    Document(page_content="Wedding planning services including venue booking, catering, and decoration", 
                            metadata={"type": "service", "source": "default"}),
                    Document(page_content="Corporate event management for conferences, seminars, and team building", 
                            metadata={"type": "service", "source": "default"}),
                    Document(page_content="Party supplies rental including tables, chairs, and sound systems", 
                            metadata={"type": "product", "source": "default"})
                ]
            
            # Create and persist vector store
            db = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=persist_directory
            )
            db.persist()
            logger.info(f"Created new ChromaDB with {len(documents)} documents")
            return db
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise

    def run(self, query: str) -> str:
        """Process the RAG query to retrieve relevant product/service information."""
        try:
            if self.rag_chain is None:
                return "I'm sorry, but I'm currently unable to access product information. Please contact support for assistance."
            
            result = self.rag_chain({"query": f"Find relevant products or services for: {query}"})
            
            # Format the response with sources
            response = result["result"]
            if "source_documents" in result and result["source_documents"]:
                response += "\n\nBased on information from our product and service catalog."
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return "I'm sorry, I encountered an error while searching for product information. Please try rephrasing your question or contact support."
