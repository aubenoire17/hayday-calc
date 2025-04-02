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

        if choice.isdigit() and 1 <= int(choice) <= 4:
            return choice
        else:
            print("Invalid choice. Please enter 1-4.")



def get_choices(config, items_df, recipe_df):

    filter_choice = get_filter()

    if filter_choice == 1:
        get_machine(config, items_df)
    else:
        get_ingredient(config, items_df, recipe_df)
    sort_choice = get_sort()
    
    return [filter_choice, sort_choice]



def main():

    config, items_df, recipes_df, rare_ingredients = run_preprocessing()

    #display_products(config, items_df, recipes_df, rare_ingredients)

    unique_ingredients = get_unique_sorted_ingredients(recipes_df, items_df)
    get_ingredient_choice(unique_ingredients)

if __name__ == "__main__":
    main()