import pandas as pd

class Product:
    def __init__(self, name, price, time, xp, machine, ingredients=None):
        self.name = name.capitalize()
        self.price = price
        self.time = self.time_convert(time)
        self.xp = xp
        self.machine = machine
        self.ingredients = ingredients if ingredients is not None else []
        self.production_cost = self.calculate_production_cost()

    def __repr__(self):
        return (f"Product(Name: {self.name}, Price: {self.price}, Time: {self.time}, "
                f"XP: {self.xp}, Machine: {self.machine}, ProductionCost: {self.production_cost}, Ingredients: {self.ingredients})")

    @staticmethod
    def time_convert(value):
        if 'd' in value and 'h' in value:
            days = int(value[:value.find('d')].strip())
            hours = int(value[value.find('d') + 1:value.find('h')].strip())
            return (days * 24 + hours) * 60
        elif 'h' in value and 'min' in value:
            hours = int(value[:value.find('h')].strip())
            minutes = int(value[value.find('h') + 1:value.find('min')].strip())
            return hours * 60 + minutes
        elif 'd' in value:
            days = int(value[:value.find('d')].strip())
            return days * 24 * 60
        elif 'h' in value:
            hours = int(value[:value.find('h')].strip())
            return hours * 60
        elif 'min' in value:
            minutes = int(value[:value.find('min')].strip())
            return minutes
        elif 'Instant' in value:
            return 1
        else:
            return 'ERROR'
        

    def calculate_production_cost(self):
        total_cost = 0
        for ingredient in self.ingredients:
            price = pd.to_numeric(ingredient['price'], errors='coerce')
            quantity = pd.to_numeric(ingredient['quantity'], errors='coerce')
            total_cost += price * quantity
        return total_cost


# Read the main CSV file
products_df = pd.read_csv(r'C:\Users\yanso\VSCode proj\hayday\data\HDpriceandxp.csv')

# Read the ingredients CSV file
ingredients_df = pd.read_csv(r'C:\Users\yanso\VSCode proj\hayday\data\HDingredients.csv', header=None, names=['Product', 'Ingredient', 'Quantity'])

# Capitalize Product and Ingredient columns
ingredients_df['Product'] = ingredients_df['Product'].str.capitalize()
ingredients_df['Ingredient'] = ingredients_df['Ingredient'].str.capitalize()

# Create instances of the Product class
products = []

for index, row in products_df.iterrows():
    product = Product(row['Name'], row['Price'], row['Time'], row['XP'], row['Machine'])
    products.append(product)

# Create a dictionary to map product names to Product instances
product_dict = {product.name: product for product in products}

# Update the Product instances with ingredients information
for index, row in ingredients_df.iterrows():
    product_name = row['Product']
    if product_name in product_dict:
        ingredient = {
            'name': row['Ingredient'],
            'price': None,  # Initialize price
            'quantity': row['Quantity']
        }
        # Find the product with matching name and update ingredient price
        for product in products:
            if product.name == ingredient['name']:
                ingredient['price'] = product.price
                break
        
        product_dict[product_name].ingredients.append(ingredient)


# Define machines to ignore for warning
ignore_warning_machines = ['Field', 'Mine', 'Sheep', 'Cow' ,'Pig' , 'Chicken' , 'Pomegranate tree' , 'Net Maker', 'Cacao tree' , 'Lure Workbench',
                           'Apple tree', 'Raspberry bush', 'Blackberry bush', 'Coconut tree', 'Mango tree', 'Banana tree', 'Guava Tree', 'Plum tree',
                           'Orange tree', 'Peach tree', 'Lemon tree', 'Squirrel House', 'Duck Salon', 'Olive tree', 'Lobster Pool']

# Update the production cost for each product
for product in products:
    product.production_cost = product.calculate_production_cost()
    if product.production_cost == 0 and product.machine not in ignore_warning_machines:
        print(f"Warning: Product {product.name} has a production cost of 0.")
        print(f"All attributes: {product}")

'''# Print the products to verify
for product in products:
    print(product)
'''