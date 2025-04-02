# Hay Day Product Calculator

This tool helps you optimize your gameplay in [Hay Day](https://hayday.com/en) by analysing the total profit/experience **and** profit/experience per minute for all the products in **Hay Day**. It allows you to analyse by production machine or ingredient type, helping you make better decisions about which product is best to make for each machine or how to best use a certain ingredient to achieve your goals in Hay Day.

## Features

- View products by **Machine** or **Ingredient**.
- Sort products by:
  - Total Profit
  - Profit Per Minute
  - Experience Per Minute
  - Total Experience
- Displays additional information about rare ingredients used in the recipes.

## Prerequisites

Before running the tool, ensure you have the following installed:

- **Python** 3.x
- **Conda**

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/aubenoire17/hayday-calc.git
    cd hayday-calc
    ```

2. Create a conda environment (recommended):

    ```bash
    conda create --name hayday-calc python=3.8
    conda activate hayday-calc
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```


## Usage

1. **Run the tool:** After setting up the environment, run the script:

```bash
python main.py
```

2. **Choose your option:** The program will prompt you to choose between sorting products by machine or by ingredient:

```text
Choose an option to get information:
1. By Machine
2. By Ingredient
```

3. Select Sorting Method: You will then be prompted to select the sorting method for the results. The available options are:

```text
Sort by:
1. Total Profit
2. Profit Per Minute
3. Experience Per Minute
4. Total Experience
```

4. Once sorted, the products will be displayed with relevant metrics, including profit, experience, and rare ingredients used in their recipes.

## File Structure

```text
.
├── data
|    ├── items.csv            # Database containing all items in Hay Day
|    ├── recipes.csv          # Database containing all recipes in Hay Day
|    └── treesnbush.py        # Database containing information on trees and bushes
├── src 
|    ├── ingredient.py        # Displays product information by ingredient
|    ├── machine.py           # Displays product information by machine
|    ├── main.py              # Entry point to run the application
|    └── preprocessing.py     # Handles initial calculations and data processing
├── config.yaml               # Configuration file
└── README.md                 # Project documentation (this file)
```

## Dependencies
This tool relies on the following Python libraries:

- pandas: For handling and manipulating the product and recipe data.

- math: For mathematical calculations, including sorting and display formatting.

- yaml: For configuration handling.

## License
This project is open source and available under the MIT License.

## Contact
For any questions or issues, feel free to open an issue on GitHub.