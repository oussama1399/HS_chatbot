from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

class FAQAgent:
    def __init__(self, llm):
        """Initialize the FAQ agent with the provided LLM."""
        self.llm = llm
        try:
            # Create embeddings for FAQ data
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            
            # Load FAQ data and create a vector store
            self.faq_db = self._initialize_faq_database()
            
            # Setup FAQ retrieval chain
            self.faq_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.faq_db.as_retriever(search_kwargs={"k": 3})
            )
            logger.info("FAQ Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize FAQ Agent: {e}")
            self.faq_chain = None
    
    def _initialize_faq_database(self) -> Chroma:
        """Initialize the FAQ database with common questions and answers."""
        # In a real implementation, this would load from a database or structured file
        faqs = [
            Document(
                page_content="Q: What types of events do you organize? A: We organize various events including weddings, corporate gatherings, birthday parties, anniversaries, and other special occasions.",
                metadata={"type": "faq", "category": "services"}
            ),
            Document(
                page_content="Q: How far in advance should I book your services? A: We recommend booking at least 3-6 months in advance for large events like weddings, and 1-2 months for smaller events.",
                metadata={"type": "faq", "category": "booking"}
            ),
            Document(
                page_content="Q: Do you offer cancellation policies? A: Yes, we offer flexible cancellation policies. Full refunds are available up to 30 days before the event, and partial refunds up to 14 days before.",
                metadata={"type": "faq", "category": "policies"}
            ),
            Document(
                page_content="Q: Can I customize my event package? A: Absolutely! We offer fully customizable packages to meet your specific needs and preferences.",
                metadata={"type": "faq", "category": "services"}
            ),
            Document(
                page_content="Q: What is the payment schedule? A: We typically require a 25% deposit to secure your date, with 50% due one month before the event and the remaining balance due one week before.",
                metadata={"type": "faq", "category": "payment"}
            )
        ]
        
        # Create vector store from FAQs
        return Chroma.from_documents(faqs, self.embeddings)
    
    def run(self, query: str) -> str:
        """Process the FAQ query and provide a relevant answer."""
        try:
            if self.faq_chain is None:
                return "I'm sorry, but I'm having trouble accessing our FAQ database at the moment. Please try again later."
            
            # Create a prompt that focuses on finding FAQ matches
            faq_prompt = f"Based on our FAQ database, answer the following question: {query}"
            
            # Get response from FAQ chain
            response = self.faq_chain.run(faq_prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error in FAQ query: {e}")
            return "I apologize, but I couldn't find specific information about that in our FAQs. Would you like me to connect you with a team member who can help?"
