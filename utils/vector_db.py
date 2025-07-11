import chromadb
from chromadb.config import Settings
import pandas as pd
import os
import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np

class VectorDatabase:
    """Manages ChromaDB vector database for semantic search."""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "hs_catering_collection"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.logger = logging.getLogger(__name__)
        
        # Initialize ChromaDB client with simple embedding function
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize sentence transformer for embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            self.logger.warning(f"Could not load sentence transformer: {e}")
            self.embedding_model = None
        
        # Get or create collection with custom embedding function
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self._get_embedding_function(),
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            self.logger.error(f"Error creating collection: {e}")
            # Fallback to basic collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name
            )
        
        self.logger.info(f"ChromaDB initialized with collection: {collection_name}")
    
    def _get_embedding_function(self):
        """Get a simple embedding function."""
        try:
            import chromadb.utils.embedding_functions as ef
            return ef.SentenceTransformerEmbeddingFunction(model_name='all-MiniLM-L6-v2')
        except Exception as e:
            self.logger.warning(f"Could not create embedding function: {e}")
            return None
    
    def add_products_to_collection(self, products_df: pd.DataFrame):
        """Add products to ChromaDB collection."""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for _, row in products_df.iterrows():
                # Use the pre-computed rag_description
                document = row.get('rag_description', '')
                if not document:
                    # Fallback to manual construction if rag_description is missing
                    document = f"Produit: {row.get('Name', '')} | Type: {row.get('Type', '')} | Catégories: {row.get('Categories', '')} | Prix: {row.get('Regular price', '')} | Description: {row.get('Description', '')}"
                
                documents.append(document)
                
                # Metadata
                metadata = {
                    'type': 'product',
                    'id': int(row.get('ID', 0)),
                    'name': str(row.get('Name', '')),
                    'category': str(row.get('Categories', '')),
                    'price': float(row.get('Regular price_numeric', 0.0)),
                    'available': bool(row.get('is_available', False)),
                    'tags': str(row.get('Tags', '')),
                    'price_tier': str(row.get('price_tier', ''))
                }
                metadatas.append(metadata)
                ids.append(f"product_{row.get('ID', 0)}")
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"Added {len(documents)} products to ChromaDB")
            
        except Exception as e:
            self.logger.error(f"Error adding products to ChromaDB: {str(e)}")
    
    def add_services_to_collection(self, services_df: pd.DataFrame):
        """Add services to ChromaDB collection."""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for _, row in services_df.iterrows():
                # Create document from service data
                document = f"Service: {row.get('nom_service', '')} | Type: {row.get('type_service', '')} | Résumé: {row.get('résumé_service', '')} | Prix: {row.get('prix_minimum', '')} - {row.get('prix_maximum', '')} MAD | Spécialité: {row.get('spécialité', '')} | Mots-clés: {row.get('mots_clés', '')}"
                
                documents.append(document)
                
                # Metadata
                metadata = {
                    'type': 'service',
                    'name': str(row.get('nom_service', '')),
                    'service_type': str(row.get('type_service', '')),
                    'summary': str(row.get('résumé_service', '')),
                    'min_price': float(row.get('prix_minimum', 0.0)) if pd.notna(row.get('prix_minimum')) else 0.0,
                    'max_price': float(row.get('prix_maximum', 0.0)) if pd.notna(row.get('prix_maximum')) else 0.0,
                    'availability': str(row.get('statut_disponibilité', '')),
                    'specialty': str(row.get('spécialité', '')),
                    'keywords': str(row.get('mots_clés', '')),
                    'target_audience': str(row.get('public_cible', ''))
                }
                metadatas.append(metadata)
                ids.append(f"service_{row.get('nom_service', '').replace(' ', '_').lower()}")
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"Added {len(documents)} services to ChromaDB")
            
        except Exception as e:
            self.logger.error(f"Error adding services to ChromaDB: {str(e)}")
    
    def search_similar(self, query: str, n_results: int = 5, filter_type: str = None) -> List[Dict[str, Any]]:
        """Search for similar items in the collection."""
        try:
            # Prepare where clause for filtering
            where_clause = {}
            if filter_type:
                where_clause['type'] = filter_type
            
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'document': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0,
                        'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else ''
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching in ChromaDB: {str(e)}")
            return []
    
    def search_products(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for products only."""
        return self.search_similar(query, n_results, filter_type='product')
    
    def search_services(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for services only."""
        return self.search_similar(query, n_results, filter_type='service')
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = self.collection.count()
            return {
                'total_items': count,
                'collection_name': self.collection_name,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            return {'total_items': 0}
    
    def initialize_database(self, products_df: pd.DataFrame, services_df: pd.DataFrame, force_rebuild: bool = False):
        """Initialize the database with products and services data."""
        try:
            current_count = self.collection.count()
            
            if current_count == 0 or force_rebuild:
                if force_rebuild and current_count > 0:
                    # Clear existing data
                    self.client.delete_collection(self.collection_name)
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        metadata={"hnsw:space": "cosine"}
                    )
                
                # Add products and services
                self.add_products_to_collection(products_df)
                self.add_services_to_collection(services_df)
                
                self.logger.info("Database initialized successfully")
            else:
                self.logger.info(f"Database already initialized with {current_count} items")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
    
    def delete_collection(self):
        """Delete the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self.logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            self.logger.error(f"Error deleting collection: {str(e)}")
