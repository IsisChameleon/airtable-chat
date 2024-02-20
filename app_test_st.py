import streamlit as st
import pandas as pd

# Sample DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['New York', 'Los Angeles', 'Chicago']}
df = pd.DataFrame(data)

# Function to display details of the user (this can be customized)
def show_user_details(name):
    st.write(f"Details for {name}")

# Display the DataFrame with buttons
for index, row in df.iterrows():
    cols = st.columns([2, 1, 2, 1]) # Adjust the number of columns and their sizes as needed
    cols[0].write(row['Name'])
    cols[1].write(row['Age'])
    cols[2].write(row['City'])

    # Each button is unique by using the index of the DataFrame's row
    if cols[3].button(f"Details", key=f"button_{index}"):
        # This is where you can redirect to another page or show details
        # For demonstration, I'll just show details on the same page
        show_user_details(row['Name'])

# Run this with 'streamlit run your_script.py'
