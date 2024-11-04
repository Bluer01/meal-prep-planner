from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool
from flask import current_app, g, Response
from contextlib import contextmanager
from config import Config
import redis
from functools import wraps
import json
from typing import Any, Callable
import os

# Create database engine with connection pooling
engine = create_engine(
    Config.SQLITE_URI,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Create scoped session factory
Session = scoped_session(sessionmaker(bind=engine))

# Redis connection for caching
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    decode_responses=True,
    socket_connect_timeout=30,
    retry_on_timeout=True
)
def get_db():
    """Get database session."""
    if 'db' not in g:
        g.db = Session()
    return g.db

@contextmanager
def db_session():
    """Database session context manager."""
    session = get_db()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def close_db(e=None):
    """Close database session."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Initialize database with application."""
    app.teardown_appcontext(close_db)

def init_db():
    """Initialize the database."""
    from .models import Base
    Base.metadata.create_all(bind=engine)

def load_sample_recipes():
    """Load sample recipes into the database."""
    from .models import Recipe
    
    with db_session() as session:
        # Check if we have any recipes
        if session.query(Recipe).count() == 0:
            sample_recipes = [
                {
                    'name': 'Chicken Stir Fry',
                    'ingredients': [
                        {'name': 'chicken breast', 'amount': 500, 'unit': 'g'},
                        {'name': 'bell pepper', 'amount': 2, 'unit': 'whole'},
                        {'name': 'broccoli', 'amount': 300, 'unit': 'g'},
                        {'name': 'soy sauce', 'amount': 60, 'unit': 'ml'}
                    ],
                    'servings': 4,
                    'categories': ['Asian', 'High-Protein', 'Quick Meals']
                },
                {
                    'name': 'Quinoa Bowl',
                    'ingredients': [
                        {'name': 'quinoa', 'amount': 200, 'unit': 'g'},
                        {'name': 'chickpeas', 'amount': 400, 'unit': 'g'},
                        {'name': 'cucumber', 'amount': 1, 'unit': 'whole'},
                        {'name': 'cherry tomatoes', 'amount': 200, 'unit': 'g'}
                    ],
                    'servings': 3,
                    'categories': ['Vegetarian', 'Healthy', 'Meal Prep']
                }
            ]
            
            for recipe_data in sample_recipes:
                recipe = Recipe.from_dict(recipe_data)
                session.add(recipe)
            
            session.commit()

def cache(timeout: int = 300) -> Callable:
    """Cache decorator for routes that handles both JSON and regular responses."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Create cache key from function name and arguments
            cache_key = f'{f.__name__}:{str(args)}:{str(kwargs)}'
            
            # Try to get cached response
            cached_data = redis_client.get(cache_key)
            if cached_data:
                cached_dict = json.loads(cached_data)
                if cached_dict.get('_type') == 'template':
                    # Reconstruct Response object for template responses
                    return Response(
                        cached_dict['data'],
                        status=cached_dict['status'],
                        headers=cached_dict['headers'],
                        mimetype=cached_dict['mimetype']
                    )
                # Return JSON data directly
                return cached_dict.get('data')
            
            # Get fresh response
            response = f(*args, **kwargs)
            
            # Prepare data for caching based on response type
            if isinstance(response, Response):
                cache_data = {
                    '_type': 'template',
                    'data': response.get_data(as_text=True),
                    'status': response.status_code,
                    'headers': dict(response.headers),
                    'mimetype': response.mimetype
                }
            else:
                cache_data = {
                    '_type': 'json',
                    'data': response
                }
            
            # Cache the prepared data
            redis_client.setex(
                cache_key,
                timeout,
                json.dumps(cache_data)
            )
            
            return response
        return decorated_function
    return decorator