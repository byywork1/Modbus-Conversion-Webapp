import streamlit as st
import csv
from io import StringIO
from io import BytesIO
import re

def oct_to_modified_decimal_BOOL(octal_str):
    try:
        decimal_value = int(octal_str, 8)
        return decimal_value + 3072 if decimal_value <= 3777 else f"NA{octal_str}"
    except ValueError:
        return f"Invalid octal input at {octal_str}"
    
def convert_bool(address, name):
    address = oct_to_modified_decimal_BOOL(address)
    formatted_address = f'1.{address}'
    return ['boolean', name, 'high', str(formatted_address), "==", 'TRUE', 'value', 1000, 'CHANGE ME', 'Client']


def process_csv_stream(documentation_stream, variables_stream):
    # read documentation into a dict 
    documentation_reader = csv.reader(documentation_stream)
    documentation_lookup = {}

    for row in documentation_reader: 
        if len(row) < 4: 
            st.warning(f"⚠️ Documentation CSV is missing required columns.{row}")
            continue 
        address = row[0].strip().upper()
        name = row[3].strip()
        documentation_lookup[address] = name

    # Process variables 
    variables_stream.seek(0)  # Reset the stream position to the beginning
    variables = csv.DictReader(variables_stream)
   
    processed_rows = []
    missing_addresses = []
    converted_addresses = []

    for var_row in variables:
        address = var_row.get('ADDRESS', '').strip().upper() #input what other variables are input on the csv
        
        if not address: 
            continue

        if address not in documentation_lookup:
            missing_addresses.append(address)
            continue    

        numeric_address = re.sub(r'^\D+', '', address) #remove non-numeric prefix
        name = documentation_lookup.get(address)

        processed_row = convert_bool(numeric_address, name)
        
        processed_rows.append(processed_row)
        converted_addresses.append(address)

    

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Type', 'Name', 'Severity', 'Address', 'Condition', 'Threshold', 'ThresholdType', 'On delay', 'Operator instructions', 'Access category'])
    writer.writerows(processed_rows)
    output.seek(0)
    return output, missing_addresses, converted_addresses

# 🎯 Streamlit UI starts here
st.set_page_config(page_title="Alarm Conversion", page_icon="🔧", layout="centered")
st.title("Alarm Conversion :rotating_light:")

# upload files 
documentation_file = st.file_uploader("Upload your documentation CSV", type=["csv"], key = 'doc')
variables_file = st.file_uploader("Upload your alarms CSV", type=["csv"], key = 'vars')
output_filename = st.text_input("Name your output file (without .csv)")


# session state 
if 'result_csv' not in st.session_state:
    st.session_state.result_csv = None
if 'missing_addresses' not in st.session_state:
    st.session_state.missing_addresses = None

col1, col2 = st.columns(2)


with col1:
    if st.button("⚙️Convert"): # Convert Button 
        if documentation_file and variables_file: 
            with st.spinner('🔄 Converting'):
                documentation_stream = StringIO(documentation_file.getvalue().decode("utf-8"))
                variables_stream = StringIO(variables_file.getvalue().decode("utf-8"))

                result_csv, missing_addresses, converted_addresses = process_csv_stream(documentation_stream, variables_stream)

                
                if missing_addresses:
                    st.sidebar.error(f"❗ ERROR: The following addresses were not found in the documentation CSV:\n{', '.join(missing_addresses)}")
                if converted_addresses:
                    st.sidebar.success(f"✅ Conversion successful! The following addresses were converted:\n{', '.join(converted_addresses)}")
                else:
                    st.sidebar.warning("⚠️ No addresses were successfully converted.")
                
                
                st.session_state.result_csv = result_csv
                st.session_state.missing_addresses = missing_addresses


# Download Button
if st.session_state.result_csv and st.session_state.missing_addresses is not None:
    if not st.session_state.missing_addresses:  # Only show download if no missing addresses
        st.download_button(
            label="Download Converted CSV",
            data=st.session_state.result_csv.getvalue(),
            file_name=f"{output_filename}.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Please fix missing addresses before downloading.")

with col2:
    if st.button("🔄Reset"):
        st.session_state.result_csv = None
        st.session_state.missing_addresses = None
        st.session_state.documentation_file = None
        st.session_state.variables_file = None
        st.success("🧹 Reset complete! Upload new files to start again.")

st.markdown(':rotating_light: _Variables csv column headers must ALL capitalized_: **"ADDRESS"** :rotating_light:')