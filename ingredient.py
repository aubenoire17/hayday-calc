import math
import pandas as pd

from preprocessing import run_preprocessing

def get_sort():

    while True:
        print("\nSort by:")
        print("1. Total Profit")
        print("2. Profit Per Minute")
        print("3. Experience Per Minute")
        print("4. Total Experience")
        
        choice = input("Enter the number corresponding to your choice (1/2/3/4): ").strip()

        if choice.isdigit() and 1 <= int(choice) <= 4:
            return choice
        else:
            print("Invalid choice. Please enter 1-4.")

def get_unique_sorted_ingredients(recipes_df, items_df):
    ingredient_map = {row['id']: row['name'] for _, row in items_df.iterrows()}

    unique_ingredient_ids = recipes_df['ingredient'].unique()

    unique_ingredient_names = [
        ingredient_map[ingredient_id]
        for ingredient_id in unique_ingredient_ids
        if ingredient_id in ingredient_map
    ]

    return sorted(unique_ingredient_names)

def get_ingredient_choice(ingredients, num_columns=5):
    """
    Display a list of unique ingredients and get the user's selection.

    Args:
        ingredients (List[str]): Alphabetically sorted list of unique ingredient names.
        num_columns (int): Number of columns to display.

    Returns:
        str: The selected ingredient name.
    """
    num_rows = math.ceil(len(ingredients) / num_columns)
    columns = [ingredients[i:i + num_rows] for i in range(0, len(ingredients), num_rows)]

    print("Available ingredients:")
    
    max_length = max(len(ingredient) for ingredient in ingredients)
    column_width = max_length + 2
    number_width = len(str(len(ingredients))) + 2

    for row in range(num_rows):
        row_display = []
        for col in range(num_columns):
            if row < len(columns[col]):
                ingredient_name = f"{columns[col][row]}"
                index = f"{(col * num_rows) + row + 1}"
                row_display.append(f"{index:<{number_width}} {ingredient_name:<{column_width}}")
            else:
                row_display.append(' ' * (number_width + column_width))
        
        print("".join(row_display))

    while True:
        choice = input(f"\nSelect an ingredient (1-{len(ingredients)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(ingredients):
            return ingredients[int(choice) - 1]
        else:
            print(f"Invalid choice. Please enter a number between 1 and {len(ingredients)}.")

def get_products(ingredient_choice, items_df, recipes_df):
    
    id_choice = items_df[items_df['name'] == ingredient_choice]['id'].iloc[0]
    products_using_ingredient = recipes_df[recipes_df['ingredient'] == id_choice]['product']

    print(products_using_ingredient)

    product_ids_using_ingredient = recipes_df[recipes_df['ingredient'] == id_choice]['product'].unique()

    # Assuming 'id' column in items_df corresponds to product IDs and 'name' is the product name
    product_names_using_ingredient = items_df[items_df['id'].isin(product_ids_using_ingredient)]['name']

    # Printing the list of product names
    print(product_names_using_ingredient)

    return products_using_ingredient.unique()

    
def display_products(items_df, recipes_df, rare_ingredients):

    unique_ingredients = get_unique_sorted_ingredients(recipes_df, items_df)
    ingredient_choice = get_ingredient_choice(unique_ingredients)
    id_choice = items_df[items_df['name'] == ingredient_choice]['id'].iloc[0]
    product_ids_using_ingredient = recipes_df[recipes_df['ingredient'] == id_choice]['product'].unique()
    filtered_items = items_df[items_df['id'].isin(product_ids_using_ingredient)]

    print(filtered_items[['name', 'machine', 'total_profit', 'profit_per_minute', 
                    'experience_per_minute', 'experience',]].to_string())
    


def main():

    _, items_df, recipes_df, rare_ingredients = run_preprocessing()
    display_products(items_df, recipes_df, rare_ingredients)
    
if __name__ == "__main__":
    main()