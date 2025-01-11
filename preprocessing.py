import pandas as pd
import yaml


def load_config(config_file: str) -> dict:
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


def load_data(config):

    items_df = pd.read_csv(config['files']['items_csv'])
    recipes_df = pd.read_csv(config['files']['recipes_csv'])
    plants_df = pd.read_csv(config['files']['plants_csv'])

    return items_df, recipes_df, plants_df 


def convert_time(items_df):

    for index, row in items_df.iterrows():
        value = row['time']

        if 'd' in value and 'h' in value:
            days = int(value.split('d')[0].strip())
            hours = int(value.split('d')[1].split('h')[0].strip())
            items_df.at[index, 'time'] = (days * 24 + hours) * 60
        elif 'h' in value and 'min' in value: 
            hours = int(value.split('h')[0].strip()) 
            minutes = int(value.split('h')[1].split('min')[0].strip())
            items_df.at[index, 'time'] = hours * 60 + minutes
        elif 'd' in value:  # Example: "1 d"
            days = int(value.split('d')[0].strip())
            items_df.at[index, 'time'] = days * 24 * 60
        elif 'h' in value:  # Example: "8 h"
            hours = int(value.split('h')[0].strip()) 
            items_df.at[index, 'time'] = hours * 60
        elif 'min' in value:  # Example: "45 min"
            minutes = int(value.split('min')[0].strip())
            items_df.at[index, 'time'] = minutes
        elif 'Instant' in value:
            items_df.at[index, 'time'] = 0
        else:
            raise ValueError(f"Unrecognized time format: {value}")
        
    items_df['time'] = items_df['time'].round(0)

    return items_df


def calculate_machine_production_cost(items_df, recipes_df):

    product_costs = {}

    for product in recipes_df['product'].unique():
        product_recipe = recipes_df[recipes_df['product'] == product]

        total_cost = 0
        for _, row in product_recipe.iterrows():
            ingredient_cost = items_df.loc[items_df['id'] == row['ingredient'], 'cost'].values[0]
            total_cost += ingredient_cost * row['quantity']

        product_costs[product] = total_cost

    items_df['production_cost'] = items_df['id'].map(product_costs)

    return items_df


def update_cost_from_treesnbush(items_df, plants_df):

    fruit_cost_map = dict(zip(plants_df['fruit'], plants_df['plantprice']))

    items_df.loc[items_df['name'].isin(fruit_cost_map.keys()), 'production_cost'] = (
        items_df.loc[items_df['name'].isin(fruit_cost_map.keys()), 'name'].map(fruit_cost_map) / 13
    )

    # Hardcore for Honeycomb since it's a special case
    items_df.loc[items_df['name'] == 'Honeycomb', 'production_cost'] = 120 / 2.5

    return items_df

def update_feed_price(items_df, feed_to_item_map):

    feed_names = list(feed_to_item_map.keys())
    
    for feed in feed_names:
        feed_price = items_df.loc[items_df['name'] == feed, 'production_cost'].values[0]
        items_df.loc[items_df['name'] == feed, 'production_cost'] = feed_price / 3

    return items_df


def update_item_production_cost(items_df, feed_to_item_map):

    for feed, item_name in feed_to_item_map.items():
        feed_price = items_df.loc[items_df['name'] == feed, 'production_cost'].values[0]
        items_df.loc[items_df['name'] == item_name, 'production_cost'] = feed_price

    return items_df


def update_cost_for_feed(items_df, feed_to_item_map):

    items_df = update_feed_price(items_df, feed_to_item_map)
    items_df = update_item_production_cost(items_df, feed_to_item_map)

    return items_df

def update_items_with_no_cost(items_df):

    items_df.loc[items_df['machine'] == 'Field', 'production_cost'] = 0
    items_df.loc[items_df['machine'] == 'Mine', 'production_cost'] = 0
    items_df.loc[items_df['machine'] == 'Lure Workbench', 'production_cost'] = 0
    items_df.loc[items_df['machine'] == 'Net Maker', 'production_cost'] = 0
    items_df.loc[items_df['machine'] ==' Fish', 'production_cost'] = 0
    items_df.loc[items_df['machine'] == 'Duck Salon', 'production_cost'] = 0
    items_df.loc[items_df['machine'] == 'Lobster Pool', 'production_cost'] = 0

    return items_df

def calculate_production_cost(items_df, recipes_df, plants_df, config):

    items_df = calculate_machine_production_cost(items_df, recipes_df)
    items_df = update_cost_from_treesnbush(items_df, plants_df)
    items_df = update_cost_for_feed(items_df, config.get('animal_feed', {}))
    items_df = update_items_with_no_cost(items_df)

    items_df['production_cost'] = items_df['production_cost'].round(0)

    return items_df

def calculate_profit_and_experience_per_minute(items_df):

    items_df['total_profit'] = items_df['cost'] - items_df['production_cost']
    items_df['profit_per_minute'] = items_df.apply(lambda row: row['total_profit'] / row['time'] if row['time'] > 0 else 0, axis=1)
    items_df['experience_per_minute'] = items_df.apply(lambda row: row['experience'] / row['time'] if row['time'] > 0 else 0, axis=1)

    return items_df


def generate_rare_ingredients(items_df, config):
    rare_ingredients = []
    
    for category, ingredients in config.get('rare_ingredients', {}).items():
        for ingredient, is_available in ingredients.items():
            # If the ingredient is marked as False, add the corresponding product ID
            if is_available:
                # Filter items_df to find the product with the matching ingredient name
                matching_products = items_df[items_df['name'] == ingredient]
                
                # If the ingredient is found in the items_df, add its id to the excluded list
                if not matching_products.empty:
                    rare_ingredients.append(matching_products['id'].iloc[0])

    return rare_ingredients


def run_preprocessing():

    config = load_config("config.yaml")

    items_df, recipes_df, plants_df = load_data(config)

    items_df = convert_time(items_df)
    items_df = calculate_production_cost(items_df, recipes_df, plants_df, config)
    items_df = calculate_profit_and_experience_per_minute(items_df)

    rare_ingredients=generate_rare_ingredients(items_df, config)

    return config, items_df, recipes_df, rare_ingredients