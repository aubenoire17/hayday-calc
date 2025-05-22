import pandas as pd
import yaml

def load_config(config_file: str) -> dict:
    """
    Loads a configuration file in YAML format.

    Args:
        config_file (str): Path to the YAML configuration file.

    Returns:
        dict: Parsed configuration settings.
    """
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


def load_data(config):
    """
    Loads data from CSV files into DataFrames.

    Args:
        config (dict): Configuration dictionary containing file paths.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: DataFrames for 
        items, recipes, and plants.
    """
    items_df = pd.read_csv(config['files']['items_csv'])
    recipes_df = pd.read_csv(config['files']['recipes_csv'])
    plants_df = pd.read_csv(config['files']['plants_csv'])

    return items_df, recipes_df, plants_df 


def convert_time(items_df):
    """
    Converts time values in the 'time' column to minutes.

    Supports multiple formats:
        - "Xd Yh" → Converts days and hours to minutes.
        - "Xh Ymin" → Converts hours and minutes to minutes.
        - "Xd" → Converts days to minutes.
        - "Xh" → Converts hours to minutes.
        - "Xmin" → Keeps minutes as is.
        - "Instant" → Sets time to 0 minutes.

    Args:
        items_df (pd.DataFrame): DataFrame containing a 'time' column.

    Returns:
        pd.DataFrame: Updated DataFrame with 'time' converted to minutes.

    Raises:
        ValueError: If an unrecognized time format is encountered.
    """
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


def calculate_production_cost(items_df, recipes_df):
    """
    Calculates the production cost of each product based on its ingredients.

    This function computes the total cost of producing each product by summing the 
    costs of its ingredients, considering their respective quantities in the recipe.

    Args:
        items_df (pd.DataFrame): DataFrame containing item details, including 'item_id' and 'cost'.
        recipes_df (pd.DataFrame): DataFrame containing recipe details, with 'product', 
            'ingredient', and 'quantity' columns.

    Returns:
        pd.DataFrame: Updated `items_df` with an additional 'production_cost' column.

    Raises:
        IndexError: If an ingredient in `recipes_df` is not found in `items_df`.
    """

    product_costs = {}

    for product in recipes_df['product'].unique():
        product_recipe = recipes_df[recipes_df['product'] == product]
        total_cost = 0

        for _, row in product_recipe.iterrows():

            if not any(items_df['name'] == row['ingredient']): 
                raise ValueError(f"Ingredient '{row['ingredient']}' in recipes_df is missing from items_df")

            ingredient_cost = items_df.loc[items_df['name'] == row['ingredient'], 'cost'].values[0]
            total_cost += ingredient_cost * row['quantity']

        product_costs[product] = total_cost

    items_df['production_cost'] = items_df['name'].map(product_costs)

    return items_df

def update_cost_from_treesnbush(items_df, plants_df):
    """ 
    Updates the production cost of items based on tree and bush plant prices.

    This function assigns production costs to fruits by mapping their corresponding 
    plant prices from `plants_df`, dividing by 13 (max number of fruits you can get 
    from one tree/bush). It also includes a special case for Honeycomb, setting its 
    cost manually.

    Args:
        items_df (pd.DataFrame): DataFrame containing item details, including 'name' 
            and 'production_cost'.
        plants_df (pd.DataFrame): DataFrame containing plant details, including 'fruit' 
            and 'plantprice'.

    Returns:
        pd.DataFrame: Updated `items_df` with modified 'production_cost' values.

    Raises:
        ValueError: If a fruit in `plants_df` is not found in `items_df`.
    """
    if (missing_fruits := plants_df.loc[~plants_df['fruit'].isin(items_df['name']), 'fruit'].unique()).size > 0: 
        raise ValueError(f"Fruits in plants_df not found in items_df: {', '.join(missing_fruits)}")

    fruit_cost_map = dict(zip(plants_df['fruit'], plants_df['plantprice']))

    items_df.loc[items_df['name'].isin(fruit_cost_map.keys()), 'production_cost'] = (
        items_df.loc[items_df['name'].isin(fruit_cost_map.keys()), 'name'].map(fruit_cost_map) / 13
    )

    # Hard code for Honeycomb since it's a special case
    items_df.loc[items_df['name'] == 'Honeycomb', 'production_cost'] = 120 / 2.5

    return items_df

def update_feed_price(items_df, feed_to_item_map):
    """
    Updates the production cost of feed items by dividing their cost by 3.

    Each feed recipe produces 3 feeds. Thus a function is needed to iterate over the
    dictionary of feed items and updates their production cost by dividing their current
    production cost by 3.

    Args:
        items_df (pd.DataFrame): DataFrame containing item details, including 'name' 
            and 'production_cost'.
        feed_to_item_map (dict): Mapping of feed names to their corresponding item names.

    Returns:
        pd.DataFrame: Updated `items_df` with modified 'production_cost' values for feed items.
    """
    feed_names = list(feed_to_item_map.keys())
    
    for feed in feed_names:
        feed_price = items_df.loc[items_df['name'] == feed, 'production_cost'].values[0]
        items_df.loc[items_df['name'] == feed, 'production_cost'] = feed_price / 3

    return items_df


def update_item_production_cost(items_df, feed_to_item_map):
    """
    Updates the production cost of items based on their corresponding feed price.

    This function assigns the production cost of an item to be the same as the 
    production cost of its corresponding feed. E.g. if the cost of one chicken feed
    is 6, the price of one egg is also 6.

    Args:
        items_df (pd.DataFrame): DataFrame containing item details, including 'name' 
            and 'production_cost'.
        feed_to_item_map (dict): Mapping of feed names to their corresponding item names.

    Returns:
        pd.DataFrame: Updated `items_df` with modified 'production_cost' values for items.
    """
    for feed, item_name in feed_to_item_map.items():
        feed_price = items_df.loc[items_df['name'] == feed, 'production_cost'].values[0]
        items_df.loc[items_df['name'] == item_name, 'production_cost'] = feed_price

    return items_df


def update_cost_for_feed(items_df, feed_to_item_map):
    """
    Updates the production cost of feed items and assigns their cost to dependent items.

    This function first updates the cost of feed items by dividing by 3 
    and then assigns the feed costs to the corresponding items in `items_df`.

    Args:
        items_df (pd.DataFrame): DataFrame containing item details, including 'name' 
            and 'production_cost'.
        feed_to_item_map (dict): Mapping of feed names to their corresponding item names.

    Returns:
        pd.DataFrame: Updated `items_df` with modified 'production_cost' values for feed items and dependent items.

    Raises:
        ValueError: If any feed in `feed_to_item_map` is missing from `items_df`.

    """
    if len(missing_feeds := set(feed_to_item_map.keys()) - set(items_df['name'])) > 0:
        raise ValueError(f"Feeds missing from items_df: {', '.join(missing_feeds)}")

    items_df = update_feed_price(items_df, feed_to_item_map)
    items_df = update_item_production_cost(items_df, feed_to_item_map)

    return items_df

def update_items_with_no_cost(items_df):
    """
    Assigns a production cost of 0 to items that should not have a cost.

    This function sets the production cost to 0 for items produced by specific 
    machines, such as fields, mines, and other resources that do not require 
    material costs.

    Args:
        items_df (pd.DataFrame): DataFrame containing item details, including 'machine' 
            and 'production_cost'.

    Returns:
        pd.DataFrame: Updated `items_df` with zeroed 'production_cost' for specific machines.
    """
    items_df.loc[items_df['machine'] == 'Field', 'production_cost'] = 0
    items_df.loc[items_df['machine'] == 'Mine', 'production_cost'] = 0
    items_df.loc[items_df['machine'] == 'Lure Workbench', 'production_cost'] = 0
    items_df.loc[items_df['machine'] == 'Net Maker', 'production_cost'] = 0
    items_df.loc[items_df['machine'] ==' Fish', 'production_cost'] = 0
    items_df.loc[items_df['machine'] == 'Duck Salon', 'production_cost'] = 0
    items_df.loc[items_df['machine'] == 'Lobster Pool', 'production_cost'] = 0

    return items_df

def update_costs(items_df, recipes_df, plants_df, config):
    """
    Calculates the production cost of items based on recipes, plant prices, and feed costs.

    This function updates the production cost of items using multiple sources:
    - Machine-based production costs derived from recipes.
    - Costs of fruits obtained from trees and bushes.
    - Costs of animal feed, adjusted after dividing by 3.
    - Zero-cost assignments for items from specific machines.

    Args:
        items_df (pd.DataFrame): DataFrame containing item details.
        recipes_df (pd.DataFrame): DataFrame with recipe information for crafting items.
        plants_df (pd.DataFrame): DataFrame with plant price data for fruit-based items.
        config (dict): Configuration dictionary containing mappings such as 'animal_feed'.

    Returns:
        pd.DataFrame: Updated `items_df` with the calculated 'production_cost'.
    """
    items_df = calculate_production_cost(items_df, recipes_df)
    items_df = update_cost_from_treesnbush(items_df, plants_df)
    items_df = update_cost_for_feed(items_df, config.get('animal_feed', {}))
    items_df = update_items_with_no_cost(items_df)

    items_df['production_cost'] = items_df['production_cost'].round(0)

    return items_df

def calculate_profit_and_experience_per_minute(items_df):
    """
    Calculates profit and experience gain per minute for each item.

    This function computes:
    - `total_profit` as the difference between item cost and production cost.
    - `profit_per_minute` by dividing total profit by the production time.
    - `experience_per_minute` by dividing experience gained by production time.

    Items with zero production time are assigned a per-minute value of zero to avoid division errors.

    Args:
        items_df (pd.DataFrame): DataFrame containing item details, including 'cost', 
            'production_cost', 'time', and 'experience'.

    Returns:
        pd.DataFrame: Updated `items_df` with calculated 'total_profit', 'profit_per_minute', 
        and 'experience_per_minute' columns.
    """
    items_df['total_profit'] = items_df['cost'] - items_df['production_cost']
    items_df['profit_per_minute'] = items_df.apply(lambda row: row['total_profit'] / row['time'] if row['time'] > 0 else 0, axis=1)
    items_df['experience_per_minute'] = items_df.apply(lambda row: row['experience'] / row['time'] if row['time'] > 0 else 0, axis=1)

    return items_df


def generate_rare_ingredients(config):
    """
    Generates a list of ingredient names that are marked as rare (`True`) in the config.

    This function checks the `rare_ingredients` section of the config, and if an ingredient 
    is marked as `True`, it adds its corresponding name to the list. It does not include ingredients 
    marked as `False`.

    Args:
        items_df (pd.DataFrame): DataFrame containing item details, including 'name' and 'item_id'.
        config (dict): Configuration dictionary containing a 'rare_ingredients' section,
            which maps ingredient categories to ingredient availability.

    Returns:
        List[str]: A list of rare ingredient names.
    """
    rare_ingredients = []

    for category, ingredients in config.get('rare_ingredients', {}).items():
        for ingredient, is_rare in ingredients.items():
            if is_rare:
                rare_ingredients.append(ingredient)

    return rare_ingredients


def run_preprocessing():
    """
    Runs the full preprocessing pipeline for item, recipe, and plant data.

    This function:
    1. Loads configuration settings from 'config.yaml'.
    2. Reads the necessary CSV files into DataFrames.
    3. Converts time values in `items_df` to minutes.
    4. Updates production costs based on recipes and plant data.
    5. Computes profit per minute and experience per minute.
    6. Identifies rare ingredients based on the configuration.

    Returns:
        tuple: A tuple containing:
            - config (dict): The loaded configuration.
            - items_df (pd.DataFrame): Processed DataFrame containing item details.
            - recipes_df (pd.DataFrame): DataFrame containing recipe details.
            - rare_ingredients (List[int]): List of product IDs for rare ingredients.
    """
    config = load_config("config.yaml")

    items_df, recipes_df, plants_df = load_data(config)

    items_df = convert_time(items_df)
    items_df = update_costs(items_df, recipes_df, plants_df, config)
    items_df = calculate_profit_and_experience_per_minute(items_df)

    rare_ingredients=generate_rare_ingredients(config)

    return config, items_df, recipes_df, rare_ingredients