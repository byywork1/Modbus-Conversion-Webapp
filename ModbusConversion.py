import csv

class ModbusVariable:
    def __init__(self, Id, Name, Address, Type, Width, Signed, Unit):
        self.Id = Id 
        self.Name = Name
        self.Address = Address
        self.Type = Type
        self.Width = Width
        self.Signed = Signed
        self.Unit = Unit

    
def oct_to_modified_decimal_BOOL(octal_str):

    return f'reached octal conversion step{octal_str}'
    # try:
    #     # Convert octal string to decimal
    #     decimal_value = int(octal_str, 8)
        
    #     if decimal_value < 9999:
    #         return decimal_value + 30000
    #     else:
    #         return decimal_value + 300000
            
    # except ValueError:
    #     return f"Invalid octal input at {octal_str}"


def oct_to_modified_decimal_INT(octal_str): 
    try: 
        # Convert octal string to decimal 
        decimal_value = int(octal_str, 8)

        if decimal_value > 3777: 
            return f"NA{octal_str}"
        else: 
            return decimal_value + 3072
    
    except ValueError: 
        return f"Invalid octal input at {octal_str}"
        

    # Convert octal to float 
        
def slugify(text: str):
    return text.lower().strip().replace(" ", "-").replace(",", "").replace("/", "-").replace("--", "-")

def convert_bool(address, name): # IN: input file, address # OUT: [description, name, address, type]
    description = slugify(name)
    address = oct_to_modified_decimal_BOOL(address)
    
    return [description, name, address, 'bool', None, None, None, None, None]

def convert_int(address, name): # IN: address, name # OUT: [description, name, address, type, width, signed, , , Unit(optional)] 
    description = slugify(name)
    address = oct_to_modified_decimal_INT(address)
    
    return [description, name, address, 'int', 16, None, None, None, None] #still need to add unit and signed 

def process_csv(input_file, output_file, conversion_type, start_range, end_range):
    processed_rows = []

    with open(input_file, newline='') as csvfile:
        reader = csv.reader(csvfile)

        processing = False # flag to indicate that we are processing
        for row in reader:

            raw_identifier = row[0].strip()
            # Range filtering
            if row[0] == start_range:
                processing = True 
            elif row[0] == end_range:
                processing = False

            if processing:
                try:
                    numeric_address = raw_identifier[1:] # strip leading V
                except ValueError:
                    print(f"Invalid octal address: {raw_identifier}. Skipping row.")
                    continue  # skip invalid addresses

                # Convert based on type
                if conversion_type.upper() == "BOOL":
                    processed_row = convert_bool(numeric_address, row[3].strip())
                elif conversion_type.upper() == "INT":
                    processed_row = convert_int(numeric_address, row[3].strip())
                # add float conversion here 

                processed_rows.append(processed_row)
            
            else:
                # If not processing, skip the row
                continue

    with open(output_file, 'w', newline='') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(['Identifier', 'Name', 'Address', 'Type', 'Width', 'Signed', 'Max string length', 'Factor', 'Unit'])
        writer.writerows(processed_rows)



    

if __name__ == "__main__":
    print("📄 Modbus CSV Converter")

    input_file = input("Enter the path to the input CSV file: ").strip()
    output_file = input("Enter the desired output CSV file name: ").strip()
    conversion_type = input("Enter conversion type (BOOL or INT): ").strip().upper() #TEMP

    use_range = input("Do you want to filter by an address range? (y/n): ").strip().lower() # TEMP until better understanding of data

    start_range = end_range = None

    if use_range == 'y':
        start_range = input("Enter start of octal address range (e.g., V13200): ").strip().upper()
        end_range = input("Enter end of octal address range (e.g., V13250): ").strip().upper()

    process_csv(input_file, output_file, conversion_type, start_range, end_range)
    print(f"✅ Done! Output written to: {output_file}")

