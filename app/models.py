from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
import json
from typing import List, Set, Dict, Any
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    ingredients = Column(Text, nullable=False)
    servings = Column(Integer, nullable=False)
    categories = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    @property
    def ingredients_list(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.ingredients)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding ingredients for recipe {self.id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error accessing ingredients for recipe {self.id}: {e}")
            return []

    @property
    def categories_set(self) -> Set[str]:
        try:
            return set(json.loads(self.categories))
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding categories for recipe {self.id}: {e}")
            return set()
        except Exception as e:
            logger.error(f"Unexpected error accessing categories for recipe {self.id}: {e}")
            return set()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recipe':
        """
        Create a Recipe instance from a dictionary.
        
        Args:
            data: Dictionary containing recipe data with keys:
                - name: str
                - ingredients: List[Dict[str, Any]]
                - servings: int
                - categories: List[str] (optional)
                
        Returns:
            Recipe: New Recipe instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            # Validate required fields
            if not data.get('name'):
                raise ValueError("Recipe name is required")
            
            if not isinstance(data.get('servings'), int) or data['servings'] < 1:
                raise ValueError("Valid servings number is required")
            
            if not isinstance(data.get('ingredients'), list) or not data['ingredients']:
                raise ValueError("At least one ingredient is required")
            
            # Validate each ingredient
            for i, ingredient in enumerate(data['ingredients']):
                if not isinstance(ingredient, dict):
                    raise ValueError(f"Ingredient {i+1} must be a dictionary")
                if not ingredient.get('name'):
                    raise ValueError(f"Ingredient {i+1} name is required")
                if not isinstance(ingredient.get('amount'), (int, float)) or ingredient['amount'] <= 0:
                    raise ValueError(f"Ingredient {i+1} must have a valid amount")
                if not isinstance(ingredient.get('unit'), str):
                    raise ValueError(f"Ingredient {i+1} must have a valid unit")
            
            # Create Recipe instance
            return cls(
                name=data['name'],
                ingredients=json.dumps(data['ingredients']),
                servings=data['servings'],
                categories=json.dumps(data.get('categories', []))
            )
            
        except Exception as e:
            logger.error(f"Error creating recipe from dict: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Recipe instance to dictionary.
        
        Returns:
            Dict containing all recipe data
            
        Raises:
            Exception: If there's an error converting data
        """
        try:
            return {
                'id': self.id,
                'name': self.name,
                'ingredients': self.ingredients_list,
                'servings': self.servings,
                'categories': list(self.categories_set),
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
        except Exception as e:
            logger.error(f"Error converting recipe {self.id} to dict: {e}")
            raise

    def __repr__(self) -> str:
        """String representation of Recipe instance."""
        return f"<Recipe {self.id}: {self.name}>"

    def update(self, data: Dict[str, Any]) -> None:
        """
        Update recipe with new data.
        
        Args:
            data: Dictionary containing fields to update
            
        Raises:
            ValueError: If provided data is invalid
        """
        try:
            if 'name' in data:
                if not data['name']:
                    raise ValueError("Recipe name cannot be empty")
                self.name = data['name']
            
            if 'servings' in data:
                if not isinstance(data['servings'], int) or data['servings'] < 1:
                    raise ValueError("Servings must be a positive integer")
                self.servings = data['servings']
            
            if 'ingredients' in data:
                if not isinstance(data['ingredients'], list) or not data['ingredients']:
                    raise ValueError("At least one ingredient is required")
                # Validate ingredients
                for i, ingredient in enumerate(data['ingredients']):
                    if not isinstance(ingredient, dict):
                        raise ValueError(f"Ingredient {i+1} must be a dictionary")
                    if not ingredient.get('name'):
                        raise ValueError(f"Ingredient {i+1} name is required")
                    if not isinstance(ingredient.get('amount'), (int, float)) or ingredient['amount'] <= 0:
                        raise ValueError(f"Ingredient {i+1} must have a valid amount")
                    if not isinstance(ingredient.get('unit'), str):
                        raise ValueError(f"Ingredient {i+1} must have a valid unit")
                self.ingredients = json.dumps(data['ingredients'])
            
            if 'categories' in data:
                if not isinstance(data['categories'], list):
                    raise ValueError("Categories must be a list")
                self.categories = json.dumps(data['categories'])
                
        except Exception as e:
            logger.error(f"Error updating recipe {self.id}: {e}")
            raise