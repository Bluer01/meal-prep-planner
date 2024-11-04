// Global state
let recipes = [];
let selectedRecipes = new Map();
let categories = new Set();

// Utility functions
function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    const bgColor = type === 'error' ? 'bg-red-100 border-red-400 text-red-700' : 'bg-green-100 border-green-400 text-green-700';
    
    notification.innerHTML = `
        <div class="p-4 ${bgColor} border rounded-md shadow-sm">
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        notification.innerHTML = '';
    }, 3000);
}

// CSRF handling
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (!meta) {
        console.error('CSRF token meta tag not found');
        return '';
    }
    return meta.content;
}

// Recipe form handling
function addIngredientInput() {
    const container = document.getElementById('ingredientInputs');
    const div = document.createElement('div');
    div.className = 'flex items-center space-x-2';
    div.innerHTML = `
        <input type="text" 
               placeholder="Ingredient name" 
               class="flex-grow border border-gray-300 rounded-md shadow-sm p-2" 
               required>
        <input type="number" 
               placeholder="Amount" 
               class="w-24 border border-gray-300 rounded-md shadow-sm p-2" 
               required 
               min="0" 
               step="0.01">
        <input type="text" 
               placeholder="Unit" 
               class="w-24 border border-gray-300 rounded-md shadow-sm p-2" 
               required>
        <button type="button" 
                onclick="this.parentElement.remove()" 
                class="text-red-500 hover:text-red-700 px-2 py-1">×</button>
    `;
    container.appendChild(div);
}

// Category handling
function addCustomCategory() {
    const newCategoryInput = document.getElementById('newCategory');
    const newCategory = newCategoryInput.value.trim();
    
    if (newCategory && !categories.has(newCategory)) {
        categories.add(newCategory);
        updateCategoryFilters();
        const recipeCategoryInputs = document.getElementById('recipeCategoryInputs');
        const label = document.createElement('label');
        label.className = 'inline-flex items-center mr-4';
        label.innerHTML = `
            <input type="checkbox" value="${newCategory}" class="form-checkbox h-4 w-4">
            <span class="ml-2">${newCategory}</span>
        `;
        recipeCategoryInputs.insertBefore(label, document.getElementById('newCategoryContainer'));
    }
    newCategoryInput.value = '';
}

function updateCategoryFilters() {
    const filterContainer = document.getElementById('categoryFilters');
    filterContainer.innerHTML = Array.from(categories).map(category => `
        <label class="inline-flex items-center mr-4 mb-2">
            <input type="checkbox" 
                   value="${category}"
                   onchange="filterRecipes()"
                   class="form-checkbox h-4 w-4 text-blue-600">
            <span class="ml-2">${category}</span>
        </label>
    `).join('');
}

// Recipe list handling
function displayRecipes() {
    const recipeList = document.getElementById('recipeList');
    
    if (!recipes || recipes.length === 0) {
        recipeList.innerHTML = `
            <div class="p-4 text-gray-500 text-center border border-gray-200 rounded-lg">
                No recipes found. Add your first recipe using the form below.
            </div>
        `;
        return;
    }
    
    recipeList.innerHTML = recipes.map(recipe => {
        const isSelected = selectedRecipes.has(recipe.id);
        const currentServings = isSelected ? selectedRecipes.get(recipe.id).servings : recipe.servings;
        
        return `
            <div class="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg ${isSelected ? 'bg-blue-50' : 'bg-white'}">
                <input type="checkbox" 
                       onchange="toggleRecipe(${recipe.id})" 
                       ${isSelected ? 'checked' : ''}
                       class="h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500">
                <div class="flex-grow">
                    <h3 class="font-medium text-gray-900">${recipe.name}</h3>
                    <div class="mt-1 flex flex-wrap gap-2">
                        ${recipe.categories.map(cat => 
                            `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                ${cat}
                            </span>`
                        ).join('')}
                    </div>
                </div>
                <input type="number" 
                       value="${currentServings}"
                       min="1"
                       onchange="updateServings(${recipe.id}, this.value)"
                       class="w-20 p-2 border border-gray-300 rounded-md shadow-sm">
            </div>
        `;
    }).join('');
    
    console.log('Displayed recipes:', recipes.length);
}

function toggleRecipe(recipeId) {
    const recipe = recipes.find(r => r.id === recipeId);
    if (!recipe) return;
    
    if (selectedRecipes.has(recipeId)) {
        selectedRecipes.delete(recipeId);
    } else {
        selectedRecipes.set(recipeId, {
            id: recipeId,
            servings: recipe.servings
        });
    }
    displayRecipes();
}

function updateServings(recipeId, servings) {
    const servingsNum = parseInt(servings);
    if (servingsNum < 1) return;
    
    if (selectedRecipes.has(recipeId)) {
        selectedRecipes.set(recipeId, {
            id: recipeId,
            servings: servingsNum
        });
    }
}

// Recipe filtering
function filterRecipes() {
    const selectedCategories = Array.from(document.querySelectorAll('#categoryFilters input:checked'))
        .map(input => input.value);
    
    const queryString = selectedCategories
        .map(cat => `category=${encodeURIComponent(cat)}`)
        .join('&');
    
    fetch(`/recipes?${queryString || ''}`)
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch filtered recipes');
            return response.json();
        })
        .then(data => {
            recipes = data;
            // Update selected recipes to maintain only valid selections
            const validRecipeIds = new Set(recipes.map(r => r.id));
            for (const [recipeId] of selectedRecipes) {
                if (!validRecipeIds.has(recipeId)) {
                    selectedRecipes.delete(recipeId);
                }
            }
            displayRecipes();
        })
        .catch(error => {
            console.error('Filter error:', error);
            showNotification('Failed to filter recipes. Please try again.', 'error');
        });
}

// Recipe form submission
document.getElementById('addRecipeForm').onsubmit = function(e) {
    e.preventDefault();
    
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        showNotification('Security token missing. Please refresh the page.', 'error');
        return;
    }
    
    showLoading();
    
    const ingredientInputs = document.getElementById('ingredientInputs').children;
    const ingredients = [];
    
    for (let input of ingredientInputs) {
        const [name, amount, unit] = input.getElementsByTagName('input');
        ingredients.push({
            name: name.value,
            amount: parseFloat(amount.value),
            unit: unit.value
        });
    }

    const selectedCategories = Array.from(
        document.getElementById('recipeCategoryInputs')
        .getElementsByTagName('input'))
        .filter(input => input.checked)
        .map(input => input.value);

    const recipe = {
        name: document.getElementById('recipeName').value,
        servings: parseInt(document.getElementById('servings').value),
        ingredients: ingredients,
        categories: selectedCategories
    };

    console.log('Submitting recipe:', recipe);

    fetch('/recipes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify(recipe)
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 403) {
                throw new Error('Security token invalid. Please refresh the page.');
            }
            return response.json().then(data => {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Recipe added successfully:', data);
        
        return fetch('/recipes', {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to fetch updated recipes');
        return response.json();
    })
    .then(data => {
        console.log('Fetched updated recipes:', data);
        recipes = data;
        displayRecipes();
        
        // Reset form
        e.target.reset();
        document.getElementById('ingredientInputs').innerHTML = '';
        addIngredientInput();
        
        showNotification('Recipe added successfully');
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(error.message || 'Failed to add recipe. Please try again.', 'error');
    })
    .finally(() => {
        hideLoading();
    });
};

// Calculate ingredients
function calculateIngredients() {
    if (selectedRecipes.size === 0) {
        showNotification('Please select at least one recipe first.', 'error');
        return;
    }

    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        showNotification('Security token missing. Please refresh the page.', 'error');
        return;
    }

    const selectedRecipesArray = Array.from(selectedRecipes.values());
    
    fetch('/calculate-ingredients', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify({recipes: selectedRecipesArray})
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 403) {
                throw new Error('Security token invalid. Please refresh the page.');
            }
            throw new Error('Failed to calculate ingredients');
        }
        return response.json();
    })
    .then(ingredients => {
        const shoppingList = document.getElementById('shoppingList');
        if (ingredients.length === 0) {
            shoppingList.innerHTML = '<div class="text-gray-500">No ingredients to display</div>';
            return;
        }
        
        shoppingList.innerHTML = ingredients.map(ingredient => `
            <div class="flex justify-between p-2 border-b">
                <span>${ingredient.name}</span>
                <span>${ingredient.amount.toFixed(2)} ${ingredient.unit}</span>
            </div>
        `).join('');
    })
    .catch(error => {
        console.error('Calculation error:', error);
        showNotification(error.message || 'Failed to calculate ingredients. Please try again.', 'error');
    });
}

// Initialize application
async function initializeApp() {
    try {
        showLoading();
        console.log('Fetching initial data...');
        
        const [recipesData, categoriesData] = await Promise.all([
            fetch('/recipes').then(r => {
                if (!r.ok) throw new Error('Failed to fetch recipes');
                return r.json();
            }),
            fetch('/categories').then(r => {
                if (!r.ok) throw new Error('Failed to fetch categories');
                return r.json();
            })
        ]);
        
        console.log('Received initial recipes:', recipesData);
        console.log('Received categories:', categoriesData);
        
        recipes = recipesData;
        categories = new Set(categoriesData);
        
        displayRecipes();
        updateCategoryFilters();
    } catch (error) {
        console.error('Initialization error:', error);
        showNotification('Failed to initialize application. Please refresh the page.', 'error');
    } finally {
        hideLoading();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing app...');
    addIngredientInput();
    initializeApp();
});