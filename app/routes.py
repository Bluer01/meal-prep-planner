from flask import Blueprint, render_template, request, jsonify, current_app
from .models import Recipe
from .security import require_csrf, sanitize_input, limiter, generate_csrf_token
from .database import db_session, cache
from typing import List, Dict, Any
from sqlalchemy import or_
import json
import logging

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

def validate_recipe(data: Dict[str, Any]) -> List[str]:
    """Validate recipe data and return list of errors if any."""
    errors = []
    
    if not data.get('name'):
        errors.append("Recipe name is required")
    
    if not isinstance(data.get('servings'), int) or data['servings'] < 1:
        errors.append("Servings must be a positive integer")
    
    if not isinstance(data.get('ingredients'), list) or not data['ingredients']:
        errors.append("At least one ingredient is required")
    else:
        for i, ingredient in enumerate(data['ingredients']):
            if not isinstance(ingredient, dict):
                errors.append(f"Ingredient {i+1} is invalid")
                continue
            if not ingredient.get('name'):
                errors.append(f"Ingredient {i+1} name is required")
            if not isinstance(ingredient.get('amount'), (int, float)) or ingredient['amount'] <= 0:
                errors.append(f"Ingredient {i+1} amount must be a positive number")
            if not isinstance(ingredient.get('unit'), str) or not ingredient['unit']:
                errors.append(f"Ingredient {i+1} unit is required")
    
    if not isinstance(data.get('categories', []), list):
        errors.append("Categories must be a list")
    
    return errors

@bp.route('/')
def index():
    """Home page route with CSRF token."""
    with db_session() as session:
        categories = session.query(Recipe.categories).distinct().all()
        unique_categories = set()
        for cat_json in categories:
            cats = json.loads(cat_json[0])
            unique_categories.update(cats)
        return render_template('index.html', 
                             categories=sorted(list(unique_categories)),
                             csrf_token=generate_csrf_token())

@bp.route('/recipes', methods=['POST'])
@require_csrf
@limiter.limit("20 per minute")
def add_recipe():
    data = sanitize_input(request.get_json())
    logger.info(f"Received recipe data: {data}")
    
    errors = validate_recipe(data)
    if errors:
        logger.error(f"Validation errors: {errors}")
        return jsonify({
            'status': 'error',
            'message': 'Validation failed',
            'errors': errors
        }), 400
    
    try:
        with db_session() as session:
            recipe = Recipe.from_dict(data)
            session.add(recipe)
            session.commit()
            logger.info(f"Successfully added recipe with ID: {recipe.id}")
            
            return jsonify({
                'status': 'success',
                'message': 'Recipe added successfully',
                'recipe_id': recipe.id
            })
    except Exception as e:
        logger.error(f"Error adding recipe: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to add recipe'
        }), 500

@bp.route('/recipes', methods=['GET'])
@limiter.limit("100 per minute")
def get_recipes():
    """API route returning JSON - removed cache temporarily for debugging."""
    categories = request.args.getlist('category')
    filter_type = request.args.get('filter_type', 'OR')
    
    try:
        with db_session() as session:
            query = session.query(Recipe)
            
            if categories:
                if filter_type == 'AND':
                    for category in categories:
                        query = query.filter(Recipe.categories.contains(category))
                else:  # OR
                    conditions = [Recipe.categories.contains(category) for category in categories]
                    query = query.filter(or_(*conditions))
            
            recipes = query.all()
            logger.info(f"Fetched {len(recipes)} recipes")
            return jsonify([recipe.to_dict() for recipe in recipes])
    except Exception as e:
        logger.error(f"Error fetching recipes: {str(e)}")
        return jsonify([])

@bp.route('/calculate-ingredients', methods=['POST'])
@require_csrf
@limiter.limit("50 per minute")
def calculate_ingredients():
    data = request.get_json()
    logger.info(f"Calculating ingredients for recipes: {data}")
    
    if not isinstance(data.get('recipes'), list):
        logger.error("Invalid request format - recipes not a list")
        return jsonify({
            'status': 'error',
            'message': 'Invalid request format'
        }), 400
    
    if not data['recipes']:
        return jsonify([])
    
    total_ingredients = {}
    
    try:
        with db_session() as session:
            for recipe_selection in data['recipes']:
                if not isinstance(recipe_selection.get('servings'), (int, float)) or recipe_selection['servings'] < 0:
                    logger.error(f"Invalid servings for recipe {recipe_selection.get('id')}")
                    return jsonify({
                        'status': 'error',
                        'message': f'Invalid servings for recipe {recipe_selection.get("id")}'
                    }), 400
                
                recipe = session.query(Recipe).get(recipe_selection['id'])
                if not recipe:
                    logger.error(f"Recipe {recipe_selection['id']} not found")
                    return jsonify({
                        'status': 'error',
                        'message': f'Recipe {recipe_selection["id"]} not found'
                    }), 404
                
                multiplier = recipe_selection['servings'] / recipe.servings
                
                for ingredient in recipe.ingredients_list:
                    key = f"{ingredient['name']}_{ingredient['unit']}"
                    if key not in total_ingredients:
                        total_ingredients[key] = {
                            'name': ingredient['name'],
                            'amount': 0,
                            'unit': ingredient['unit']
                        }
                    total_ingredients[key]['amount'] += ingredient['amount'] * multiplier
            
            # Round amounts to 2 decimal places
            for ingredient in total_ingredients.values():
                ingredient['amount'] = round(ingredient['amount'], 2)
            
            logger.info(f"Successfully calculated ingredients: {list(total_ingredients.values())}")
            return jsonify(list(total_ingredients.values()))
    except Exception as e:
        logger.error(f"Error calculating ingredients: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to calculate ingredients'
        }), 500

@bp.route('/categories', methods=['GET'])
@limiter.limit("200 per minute")
def get_categories():
    try:
        with db_session() as session:
            categories = session.query(Recipe.categories).distinct().all()
            unique_categories = set()
            for cat_json in categories:
                cats = json.loads(cat_json[0])
                unique_categories.update(cats)
            logger.info(f"Fetched {len(unique_categories)} unique categories")
            return jsonify(sorted(list(unique_categories)))
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return jsonify([])