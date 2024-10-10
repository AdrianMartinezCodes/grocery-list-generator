import random

def pick_random_recipes(recipes, num_recipes, include_desserts=True):
    # Filter recipes based on dessert flag
    available_recipes = {
        recipe_name: recipe_data for recipe_name, recipe_data in recipes.items()
        if include_desserts or not recipe_data.get('dessert', False)
    }
    
    # Ensure we don't request more recipes than available
    if num_recipes > len(available_recipes):
        raise ValueError(f"Requested {num_recipes} recipes, but only {len(available_recipes)} available.")
    
    # Randomly pick the requested number of recipes
    selected_recipe_names = random.sample(list(available_recipes.keys()), num_recipes)
    
    # Convert back to a dictionary with full recipe data
    selected_recipes = {name: available_recipes[name] for name in selected_recipe_names}
    return selected_recipes
