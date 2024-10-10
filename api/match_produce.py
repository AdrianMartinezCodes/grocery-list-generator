import json
import re

from rapidfuzz import fuzz 
import inflect

from pick_recipes import pick_random_recipes

p = inflect.engine()

def match_produce():
    with open('./item_dump.json','r') as file:
        produce_lst = json.load(file)
    with open('./recipes.json','r') as file:
        recipes = json.load(file)
    randomized_recipes = pick_random_recipes(recipes,2,False)
    return calculate_grocery_list(randomized_recipes,produce_lst,False)

with open('conversion_factors.json', 'r') as f:
    conversion_factors = json.load(f)

def parse_quantity(quantity_str):
    try:
        return eval(str(quantity_str))
    except:
        return None

# Generic unit conversion function based on conversion_factors.json
def convert_unit(ingredient_name, quantity, recipe_unit, master_unit):
    recipe_unit = recipe_unit.lower()
    master_unit = master_unit.lower()
    
    conversions = conversion_factors.get('conversions', {}).get(ingredient_name.lower(), {})
    
    conversion_key = f"{recipe_unit}_to_{master_unit}"
    
    # Return the converted quantity or default to no conversion (1-to-1)
    return quantity * conversions.get(conversion_key, 1)


def find_best_match(name, master_produce_list):
    name_singular = p.singular_noun(name) or name  # Singularize the name
    best_match = None
    highest_ratio = 0

    for item in master_produce_list:
        item_name = item['name'].lower()
        ratio = fuzz.ratio(name_singular.lower(), item_name)

        # Additionally check for substring matches
        if name_singular.lower() in item_name or item_name in name_singular.lower():
            ratio = 100  # Set to maximum if one is a substring of the other

        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = item
    return best_match if highest_ratio >= 80 else None  # Only return if above threshold


# Main function to handle unit conversion, aggregation, and cost calculation
def calculate_grocery_list(recipes, master_produce_list, include_desserts=True):
    produce_totals = {}
    total_cost = 0.0
    selected_recipes = []
    for recipe_name, recipe in recipes.items():
        # Skip desserts if we're not including them
        if not include_desserts and recipe.get('Dessert', False):
            continue

        for ingredient in recipe['ingredients']:
            if ingredient['category'] != 'produce':
                continue
            name = ingredient['name']
            # Find the best matching produce item from the master list
            best_match = find_best_match(name, master_produce_list)
            if not best_match:
                continue
            
            quantity = parse_quantity(ingredient['quantity'])
            recipe_unit = ingredient['unit'].lower()
            master_unit = best_match['unit'].lower()

            # Calculate cost based on original unit price
            original_price_per_unit = float(best_match['price'].replace('$', ''))
            
            # Convert units if necessary
            if recipe_unit != master_unit:
                # Calculate the cost before conversion
                cost_before_conversion = convert_unit(name, quantity, recipe_unit, master_unit)/float(best_match['price'].replace('$', ''))
                # Convert the quantity
                quantity = convert_unit(ingredient['name'], quantity, recipe_unit, master_unit)
                print(f"ingrediant: {name} Cost_before: {cost_before_conversion}, converted qunaitty: {quantity}, original: {best_match['price']}")
                # Add to total cost based on the converted quantity
                total_cost += quantity * cost_before_conversion
                print(total_cost)
                # Update produce totals
                if name in produce_totals:
                    produce_totals[name]['total_quantity'] += quantity
                else:
                    produce_totals[name] = {
                        'total_quantity': quantity,
                        'original_price_per_unit': best_match['price'],  # Store original price for reference
                        'unit': master_unit
                    }
            else:
                # If units match, simply calculate cost and update totals
                total_cost += original_price_per_unit * quantity
                if name in produce_totals:
                    produce_totals[name]['total_quantity'] += quantity
                else:
                    produce_totals[name] = {
                        'total_quantity': quantity,
                        #'original_price_per_unit': best_match['price'],
                        'unit': master_unit
                    }
        selected_recipes.append(recipe_name)
    return {
        'produce_totals': produce_totals,
        'total_cost': round(total_cost, 2),
        'recipes': selected_recipes
    }

if __name__=="__main__":
    with open('output.json','w') as file:
        json.dump(match_produce(),file)
    
    