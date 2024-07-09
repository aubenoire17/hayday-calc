import pandas as pd

class Product:
    def __init__(self, name, price, time, xp, machine):
        self.name = name
        self.price = price
        self.time = time
        self.xp = xp
        self.machine = machine

    def __repr__(self):
        return f"Product(Name: {self.name}, Price: {self.price}, Time: {self.time}, XP: {self.xp}, Machine: {self.machine})"

# Read the CSV file
df = pd.read_csv('/path/to/your/csvfile.csv')

# Create instances of the Product class
products = []

for index, row in df.iterrows():
    product = Product(row['Name'], row['Price'], row['Time'], row['XP'], row['Machine'])
    products.append(product)

# Print the products to verify
for product in products:
    print(product)