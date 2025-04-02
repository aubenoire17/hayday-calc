import math
import pandas as pd

from preprocessing import run_preprocessing

def get_machine(available_machines, num_columns=3):

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

    input_value = input(f"\nSelect a machine (1-{len(available_machines)}): ").strip()

    if not input_value:
        return -1
    else:
        try:
            return int(input_value) - 1
        except ValueError:
            print("Invalid input. Defaulting to -1.")
            return -1
    
def get_sort():

    print("\nSort by:")
    print("1. Total Profit")
    print("2. Profit Per Minute")
    print("3. Experience Per Minute")
    print("4. Total Experience")
    
    input_value = input("Enter the number corresponding to your choice (1/2/3/4): ").strip()
    
    if not input_value:
        sort_choice = 1
    else:
        try:
            sort_choice = int(input_value)
        except ValueError:
            print("Invalid input. Defaulting to 1.")
            sort_choice = 1
        
    sort_mapping = {
        1: 'total_profit',
        2: 'profit_per_minute',
        3: 'experience_per_minute',
        4: 'experience'
    }

    return sort_mapping.get(sort_choice, 'total_profit')

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

    rare_ingredient_ids = items_df[items_df['name'].isin(rare_ingredients)]['id'].tolist()

    filtered_recipes = recipes_df[recipes_df['product'].isin(sorted_machine_data['id'])]

    rare_recipe_agg = (
        filtered_recipes[filtered_recipes['ingredient'].isin(rare_ingredient_ids)]
        .merge(items_df[['id', 'name']], left_on='ingredient', right_on='id', how='left')
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
            rare_recipe_agg, left_on='id', right_on='product', how='left'
        )
        sorted_machine_data.drop(columns=['product'], inplace=True)
    else:
        sorted_machine_data['rare_ingredients'] = ''

    sorted_machine_data['rare_ingredients'].fillna('', inplace=True)
    
    print(sorted_machine_data[['name', 'machine', 'total_profit', 'profit_per_minute', 
                            'experience_per_minute', 'experience', 'rare_ingredients']].to_string())


    return sorted_machine_data

def display_products(config, items_df, recipes_df, rare_ingredients):

    ignore_machines = config.get('ignore_machines', [])
    
    available_machines = items_df[~items_df['machine'].isin(ignore_machines)]['machine'].unique()
    
    machine_choice = get_machine(available_machines)

    if machine_choice != -1:
        machine_data = items_df[items_df['machine'] == available_machines[machine_choice]]
        sorted_machine_data = machine_data.sort_values(by=get_sort(), ascending=False)

    else:
        sorted_machine_data = items_df[~items_df['machine'].isin(ignore_machines)] \
            .sort_values(by=['machine', get_sort()], ascending=[True, False])

        
    append_rare_ingredients(sorted_machine_data, items_df, recipes_df, rare_ingredients)
    
    return sorted_machine_data


def machine():
    config, items_df, recipes_df, rare_ingredients = run_preprocessing()
    display_products(config, items_df, recipes_df, rare_ingredients)

if __name__ == "__main__":
    machine()
