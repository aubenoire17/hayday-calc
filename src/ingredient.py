import math
import pandas as pd

from preprocessing import run_preprocessing

def get_unique_sorted_ingredients(recipes_df, items_df):
    ingredient_map = {row['item_id']: row['name'] for _, row in items_df.iterrows()}

    unique_ingredient_ids = recipes_df['ingredient_item_id'].unique()

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

def get_sort():
    """
    Prompts the user to select a sorting option for displaying product data.
    
    The user is presented with a list of sorting options, including:
    1. Total Profit
    2. Profit Per Minute
    3. Experience Per Minute
    4. Total Experience
    
    The function ensures that the user selects a valid input (1-4). If the user 
    inputs an invalid value, they will be prompted again until a valid selection 
    is made.

    Returns:
        str: The key corresponding to the selected sorting option. The returned 
             value will be one of 'total_profit', 'profit_per_minute', 
             'experience_per_minute', or 'experience'.
    """

    print("\nSort by:")
    print("1. Total Profit")
    print("2. Profit Per Minute")
    print("3. Experience Per Minute")
    print("4. Total Experience")
    
    while True:
        input_value = input("Enter the number corresponding to your choice (1/2/3/4): ").strip()
        
        if input_value in ['1', '2', '3', '4']:  # Only accept 1-4
            sort_choice = int(input_value)
            break
        else:
            print("Invalid input. Please choose a number between 1 and 4.")
    
    sort_mapping = {
        1: 'total_profit',
        2: 'profit_per_minute',
        3: 'experience_per_minute',
        4: 'experience'
    }

    return sort_mapping[sort_choice]


def append_rare_ingredients(sorted_machine_data: pd.DataFrame, 
                            items_df: pd.DataFrame, 
                            recipes_df: pd.DataFrame, 
                            rare_ingredients: list[str]) -> pd.DataFrame:
    """
    Appends a column `rare_ingredients` to `sorted_machine_data`, showing rare ingredients used.

    This function maps rare ingredient names to their IDs, filters the `recipes_df`, and aggregates 
    the rare ingredients used per product.

    Args:
        sorted_machine_data (pd.DataFrame): DataFrame containing product data.
        items_df (pd.DataFrame): DataFrame mapping ingredient IDs to names.
        recipes_df (pd.DataFrame): DataFrame listing product recipes (product, ingredient, quantity).
        rare_ingredients (List[str]): List of rare ingredient names.

    Returns:
        pd.DataFrame: Updated `sorted_machine_data` with a `rare_ingredients` column.
    """
    
    # Get the IDs of rare ingredients
    rare_ingredient_ids = items_df[items_df['name'].isin(rare_ingredients)]['item_id'].tolist()

    # Filter recipes that belong to the sorted machine data
    filtered_recipes = recipes_df[recipes_df['product_item_id'].isin(sorted_machine_data['item_id'])]

    rare_recipe_agg = (
        filtered_recipes[filtered_recipes['ingredient_item_id'].isin(rare_ingredient_ids)]
        .merge(items_df[['item_id', 'name']], left_on='ingredient_item_id', right_on='item_id', how='left')
        .groupby('product_item_id')
        .apply(
            lambda x: ', '.join(
                f"{q} {ingredient_name}" 
                for q, ingredient_name in zip(x['quantity'], x['name'])
            ),
            include_groups=False
        )
        .reset_index()
    )

    if not rare_recipe_agg.empty:
        rare_recipe_agg.rename(columns={0: 'rare_ingredients'}, inplace=True)
        sorted_machine_data = sorted_machine_data.merge(
            rare_recipe_agg, left_on='item_id', right_on='product_item_id', how='left'
        )
        sorted_machine_data.drop(columns=['product_item_id'], inplace=True)
    else:
        sorted_machine_data['rare_ingredients'] = ''

    # Fill NaN values with empty string and display the results
    sorted_machine_data['rare_ingredients'].fillna('', inplace=True)
    
    return sorted_machine_data

def display_products(items_df, recipes_df, rare_ingredients) -> None:
    """
    Displays products that use a selected ingredient, sorted by a user-defined criterion,
    and appends rare ingredients used in each product.

    The function filters products that use the chosen ingredient, sorts them based on
    a user-defined sorting option, and appends a column showing rare ingredients used.

    Args:
        items_df (pd.DataFrame): DataFrame containing information about available items.
        recipes_df (pd.DataFrame): DataFrame containing product recipes and their ingredients.
        rare_ingredients (list): List of rare ingredient names.

    Returns:
        None: This function does not return any values but directly prints the sorted product data.
    """
    
    unique_ingredients = get_unique_sorted_ingredients(recipes_df, items_df)
    ingredient_choice = get_ingredient_choice(unique_ingredients)

    id_choice = items_df[items_df['name'] == ingredient_choice]['item_id'].iloc[0]
    product_ids_using_ingredient = recipes_df[recipes_df['ingredient_item_id'] == id_choice]['product_item_id'].unique()
    filtered_items = items_df[items_df['item_id'].isin(product_ids_using_ingredient)]

    sort_criterion = get_sort()
    
    sorted_filtered_items = filtered_items.sort_values(by=sort_criterion, ascending=False)
    sorted_filtered_items = append_rare_ingredients(sorted_filtered_items, items_df, recipes_df, rare_ingredients)
    
    print(sorted_filtered_items[['name', 'machine', 'total_profit', 'profit_per_minute', 
                                 'experience_per_minute', 'experience', 'rare_ingredients']].to_string())

    

def sortby_ingredient():

    _, items_df, recipes_df, rare_ingredients = run_preprocessing()
    display_products(items_df, recipes_df, rare_ingredients)
    
if __name__ == "__main__":
    sortby_ingredient()