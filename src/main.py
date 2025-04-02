from machine import sortby_machine
from ingredient import sortby_ingredient

def main():
    while True:
        print("\nChoose an option to get information:")
        print("1. By Machine")
        print("2. By Ingredient")
        
        choice = input("Enter the number corresponding to your choice (1/2): ").strip()
        
        if choice == '1':
            sortby_machine()
            break
        elif choice == '2':
            sortby_ingredient()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()