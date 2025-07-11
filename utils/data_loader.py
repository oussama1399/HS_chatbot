import pandas as pd
import os
import json
from typing import Dict, List, Any
import logging

class DataLoader:
    """Handles loading and preprocessing of catering data."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.products_df = None
        self.services_df = None
        self.logger = logging.getLogger(__name__)
        
    def load_products(self) -> pd.DataFrame:
        """Load products data from CSV."""
        try:
            products_path = os.path.join(self.data_dir, "products_rag.csv")
            self.products_df = pd.read_csv(products_path)
            self.logger.info(f"Loaded {len(self.products_df)} products")
            return self.products_df
        except Exception as e:
            self.logger.error(f"Error loading products: {str(e)}")
            return pd.DataFrame()
    
    def load_services(self) -> pd.DataFrame:
        """Load services data from CSV."""
        try:
            services_path = os.path.join(self.data_dir, "services_rag.csv")
            self.services_df = pd.read_csv(services_path)
            self.logger.info(f"Loaded {len(self.services_df)} services")
            return self.services_df
        except Exception as e:
            self.logger.error(f"Error loading services: {str(e)}")
            return pd.DataFrame()
    
    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """Get product details by ID."""
        if self.products_df is None:
            self.load_products()
        
        product = self.products_df[self.products_df['ID'] == product_id]
        if not product.empty:
            return product.iloc[0].to_dict()
        return {}
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get products by category."""
        if self.products_df is None:
            self.load_products()
        
        products = self.products_df[
            self.products_df['Categories'].str.contains(category, case=False, na=False)
        ]
        return products.to_dict('records')
    
    def get_products_by_price_range(self, min_price: float, max_price: float) -> List[Dict[str, Any]]:
        """Get products within price range."""
        if self.products_df is None:
            self.load_products()
        
        products = self.products_df[
            (self.products_df['Regular price_numeric'] >= min_price) & 
            (self.products_df['Regular price_numeric'] <= max_price)
        ]
        return products.to_dict('records')
    
    def get_available_products(self) -> List[Dict[str, Any]]:
        """Get all available products."""
        if self.products_df is None:
            self.load_products()
        
        available = self.products_df[self.products_df['is_available'] == True]
        return available.to_dict('records')
    
    def get_service_by_name(self, service_name: str) -> Dict[str, Any]:
        """Get service by name."""
        if self.services_df is None:
            self.load_services()
        
        service = self.services_df[
            self.services_df['nom_service'].str.contains(service_name, case=False, na=False)
        ]
        if not service.empty:
            return service.iloc[0].to_dict()
        return {}
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services."""
        if self.services_df is None:
            self.load_services()
        
        return self.services_df.to_dict('records')
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Search products by name or description."""
        if self.products_df is None:
            self.load_products()
        
        # Search in multiple columns
        mask = (
            self.products_df['Name'].str.contains(query, case=False, na=False) |
            self.products_df['Description'].str.contains(query, case=False, na=False) |
            self.products_df['Categories'].str.contains(query, case=False, na=False) |
            self.products_df['Tags'].str.contains(query, case=False, na=False)
        )
        
        return self.products_df[mask].to_dict('records')
    
    def get_product_statistics(self) -> Dict[str, Any]:
        """Get product statistics."""
        if self.products_df is None:
            self.load_products()
        
        return {
            'total_products': len(self.products_df),
            'available_products': len(self.products_df[self.products_df['is_available'] == True]),
            'categories': list(self.products_df['Categories'].unique()),
            'price_range': {
                'min': self.products_df['Regular price_numeric'].min(),
                'max': self.products_df['Regular price_numeric'].max(),
                'avg': self.products_df['Regular price_numeric'].mean()
            }
        }
