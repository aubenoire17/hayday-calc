import math
import pandas as pd

from preprocessing import run_preprocessing

def get_machine_choice(available_machines, num_columns=3) -> int:
    """
    Displays a list of available machines in a grid format and prompts the user to 
    select one. The user is forced to choose a machine number between 1 and the 
    number of available machines.

    Args:
        available_machines (list): A list of machine names to choose from.
        num_columns (int): The number of columns in the displayed grid (default is 3).

    Returns:
        int: The index of the selected machine, or -1 if no valid choice is made.
    """
    num_rows = math.ceil(len(available_machines) / num_columns)
    columns = [available_machines[i:i + num_rows] for i in range(0, len(available_machines), num_rows)]
    
    print("Available machines:")
    
    max_length = max(len(machine) for machine in available_machines)
    
    column_width = max_length + 2
    number_width = len(str(len(available_machines))) + 2

    for row in range(num_rows):
        row_display = []
        for col in range(num_columns):
            if row < len(columns[col]):
                machine_name = f"{columns[col][row]}"
                index = f"{(col * num_rows) + row + 1}"
                row_display.append(f"{index:<{number_width}} {machine_name:<{column_width}}")
            else:
                row_display.append(' ' * (number_width + column_width))
        
        print("".join(row_display))

    while True:
        input_value = input(f"\nSelect a machine (1-{len(available_machines)}): ").strip()

        if not input_value:
            print("No input given. Defaulting to -1.")
            return -1
        try:
            choice = int(input_value)
            if 1 <= choice <= len(available_machines):
                return choice - 1  # Adjust for 0-based index
            else:
                print(f"Invalid choice. Please select a number between 1 and {len(available_machines)}.")
        except ValueError:
            print(f"Invalid input. Please enter a valid number between 1 and {len(available_machines)}.")

    
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

    rare_ingredient_ids = items_df[items_df['name'].isin(rare_ingredients)]['item_id'].tolist()

    filtered_recipes = recipes_df[recipes_df['product'].isin(sorted_machine_data['item_id'])]

    rare_recipe_agg = (
        filtered_recipes[filtered_recipes['ingredient'].isin(rare_ingredient_ids)]
        .merge(items_df[['item_id', 'name']], left_on='ingredient', right_on='item_id', how='left')
        .groupby('product')
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

    sorted_machine_data['rare_ingredients'] = (
        sorted_machine_data['rare_ingredients'].fillna('')
    )
    
    print(sorted_machine_data[['name', 'machine', 'total_profit', 'profit_per_minute', 
                            'experience_per_minute', 'experience', 'rare_ingredients']].to_string())

    return sorted_machine_data


def display_products(config, items_df, recipes_df, rare_ingredients):
    """
    Displays products sorted by a user-selected sorting criterion for a given machine.
    
    The function filters out machines to ignore based on the configuration, prompts 
    the user to choose a machine, and then sorts the products from the chosen machine 
    according to a user-defined sorting method. If no machine is chosen, all products 
    are displayed sorted by machine and the selected sorting criterion.

    Args:
        config (dict): Configuration containing settings like which machines to ignore.
        items_df (pd.DataFrame): DataFrame containing information about available items.
        recipes_df (pd.DataFrame): DataFrame containing product recipes.
        rare_ingredients (list): List of rare ingredients used for additional display logic.

    Returns:
        pd.DataFrame: A DataFrame containing the sorted product data based on the user's 
                      machine selection and sorting criteria.
    """
    ignore_machines = config.get('ignore_machines', [])
    
    available_machines = items_df[~items_df['machine'].isin(ignore_machines)]['machine'].unique()
    
    machine_choice = get_machine_choice(available_machines)

    if machine_choice != -1:
        machine_data = items_df[items_df['machine'] == available_machines[machine_choice]]
        sorted_machine_data = machine_data.sort_values(by=get_sort(), ascending=False)

    else:
        sorted_machine_data = items_df[~items_df['machine'].isin(ignore_machines)] \
            .sort_values(by=['machine', get_sort()], ascending=[True, False])

        
    append_rare_ingredients(sorted_machine_data, items_df, recipes_df, rare_ingredients)
    
    return sorted_machine_data


def sortby_machine():
    """
    Preprocesses data and displays products sorted by the chosen machine and sorting option.

    This function runs the preprocessing step to prepare the required data and then 
    calls the `display_products` function to display the products from the selected machine 
    sorted according to the user's chosen sorting criterion.

    Returns:
        None: This function does not return any values but directly prints the sorted products.
    """
    config, items_df, recipes_df, rare_ingredients = run_preprocessing()
    display_products(config, items_df, recipes_df, rare_ingredients)


if __name__ == "__main__":
    sortby_machine()
