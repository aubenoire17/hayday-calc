import math
import pandas as pd
import yaml

from preprocessing import run_preprocessing

def get_filter():

    while True:
        print("\nChoose an option to get information:")
        print("1. By Machine")
        print("2. By Ingredient")
        
        choice = input("Enter the number corresponding to your choice (1/2): ").strip()
        
        if choice in ['1', '2']:
            return choice
        else:
            print("Invalid choice. Please enter 1 or 2.")


def get_sort():

    while True:
        print("\nSort by:")
        print("1. Total Profit")
        print("2. Profit Per Minute")
        print("3. Experience Per Minute")
        print("4. Total Experience")
        
        choice = input("Enter the number corresponding to your choice (1/2/3/4): ").strip()

        if choice in ['1', '2', '3', '4']:
            return choice
        else:
            print("Invalid choice. Please enter 1-4.")


def get_choices():

    filter_choice = get_filter()
    sort_choice = get_sort()
    
    return [filter_choice, sort_choice]


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

def append_rare_ingredients(sorted_machine_data, items_df, recipes_df, rare_ingredients):

    sorted_machine_data['rare_ingredients'] = ''
    
    ingredient_map = {row['id']: row['name'] for _, row in items_df.iterrows()}
    
    for index, row in recipes_df.iterrows():
        product_id = row['product']
        ingredient_id = row['ingredient']
        quantity = row['quantity'] 
        
        if ingredient_id in rare_ingredients:
            if ingredient_id not in ingredient_map:
                raise ValueError(f"Ingredient ID {ingredient_id} not found in items_df!")
            
            ingredient_name = ingredient_map[ingredient_id]

            product_index = sorted_machine_data[sorted_machine_data['id'] == product_id].index
            for idx in product_index:
                current_value = sorted_machine_data.at[idx, 'rare_ingredients']
                if current_value:
                    sorted_machine_data.at[idx, 'rare_ingredients'] += f', {quantity} {ingredient_name}'
                else:
                    sorted_machine_data.at[idx, 'rare_ingredients'] = f'{quantity} {ingredient_name}'
    
    print(sorted_machine_data[['name', 'machine', 'total_profit', 'profit_per_minute', 'experience_per_minute', 'experience', 'rare_ingredients']].to_string())

    
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





'''def display_without_rare_ingredients(sorted_machine_data, recipes_df, excluded_ingredients):
    # Initialize a list to store the ids of rows to be excluded
    exclude_ids = []
    
    # Iterate through the recipes_df to check for ingredients in the excluded list
    for index, row in recipes_df.iterrows():
        product_id = row['product']  # Product id in recipes_df
        ingredient_id = row['ingredient']  # Ingredient id used in the product
        
        # If the ingredient_id is in the excluded_ingredients list, mark this product id for exclusion
        if ingredient_id in excluded_ingredients:
            exclude_ids.append(product_id)
    
    # Filter sorted_machine_data to remove rows with excluded product ids
    filtered_data = sorted_machine_data[~sorted_machine_data['id'].isin(exclude_ids)]

    #print(f"\nProducts for {selected_machine} sorted by {sort_option}:")
    print(filtered_data[['name', 'total_profit', 'profit_per_minute', 'experience_per_minute', 'experience']])

    return filtered_data'''



def main():

    config, items_df, recipes_df, rare_ingredients = run_preprocessing()

    display_products(config, items_df, recipes_df, rare_ingredients)



if __name__ == "__main__":
    main()
