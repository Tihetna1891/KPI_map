import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
import requests
import sys
sys.path.append('../')
# from scripts.Loader import DataLoader
from map import *
# def fetch_google_sheet_csv(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an HTTPError for bad responses
#         csv_data = response.content.decode('utf-8')
#         return csv_data
#     except requests.exceptions.RequestException as e:
#         st.error(f"Error fetching data: {e}")
#         return None

# def is_valid_time(time_string):
#     """
#     This function checks if a time string has a valid format (e.g., HH:MM).

#     Args:
#         time_string: String representing the time to be validated.

#     Returns:
#         True if the time string is valid, False otherwise.
#     """
#     try:
#         # Assuming HH:MM format, adjust based on your actual format
#         pd.to_datetime(time_string, format='%H:%M')
#         return True
#     except ValueError:
#         return False

# df = DataLoader("delivery_location")
# df1 = DataLoader('groups')
# df2 = DataLoader('devices')
# df0 = DataLoader('orders')
# df3 = DataLoader('groups_carts')
# df4 = DataLoader('groups')      
# df5 = DataLoader('group_deals')
# df6 = DataLoader('products')
# df7 = DataLoader('refund')
# @st.cache_data()
# def load_data(table_name):
#     return DataLoader(table_name)
# df = load_data("delivery_location")
# df1 = load_data('groups')
# df2 = load_data('devices')
# df0 = load_data('orders')
# df3 = load_data('groups_carts')
# df4 = load_data('groups')
# df5 = load_data('group_deals')
# df6 = load_data('products')
# df7 = load_data('refund')

# Convert Google Sheets URL to CSV URL
url_1 = convert_google_sheet_url("https://docs.google.com/spreadsheets/d/1BEufOLvdrC64XRC3_8fRRjtfkq3XYjVnJm3jRJV4zaI/edit?usp=sharing")
try:
    filtered_data= pd.read_csv(url_1)
    st.write("Data loaded successfully!")  # Debugging statement
except Exception as e:
    st.error(f"Failed to load data into DataFrame: {e}")
    st.stop()
tab1, tab2, tab3 = st.tabs(["Daily Report", "Past Price Trend", "Data Entry Form"])

with tab1:
    st.title("DASHBOARD")
    st.sidebar.title("SIDE BAR")
    st.markdown(" This application is a Streamlit app used to analyze ChipChip & YAZZ KPI")
    st.sidebar.markdown(" This application is a Streamlit app used to analyze KPI of ChipChip")
    # Convert 'created_at' to datetime and 'location' to a tuple of floats (latitude, longitude)
    filtered_data['created_at'] = pd.to_datetime(filtered_data['created_at'])
    filtered_data[['longitude', 'latitude']] = filtered_data['location'].str.strip('()').str.split(',', expand=True).astype(float)
    selected_date_range = st.sidebar.date_input("Select Date Range", 
                                            value=(pd.to_datetime('today') - pd.to_timedelta(7, unit='d'), 
                                                    pd.to_datetime('today')), 
                                            key="date_range")

    start_date = selected_date_range[0]
    end_date = selected_date_range[1]
    if start_date > end_date:
        st.sidebar.error("Please select a valid date range.")

    st.sidebar.subheader("Breakdown ")
    choice = st.sidebar.multiselect("Pick", ('ptatoes', 'Tomatoes', 'white cabbage', 'Dark cabbage', 'Door', 'mangos'), key='unique_key_1')
    # choice = st.sidebar.multiselect("Pick", ('ptatoes', 'Tomatoes', 'white cabbage', 'Dark cabbage', 'Door', 'mangos'), key='unique_key_1')
    
    # visualize_status_counts(df0, selected_date_range)
    # visualize_completion_time(df1, selected_date_range)
    visualize_tweets_on_map(filtered_data,selected_date_range)
    # visualize_os_distribution(df2, selected_date_range)
    # visualize_max_group_member(df0, df3, df4, df5, selected_date_range)
    # count_refund_status(df7, selected_date_range)

    # if len(choice) > 0:
    #         choice_data = data[data.airline.isin(choice)]
    #         fig_0 = px.histogram(choice_data, x='products', y='counts', histfunc='count', color='airline_sentiment', facet_col='airline_sentiment', labels={'airline_sentiment':'tweets'}, height=600, width=800)
    #         st.plotly_chart(fig_0)
    # if len(choice) > 0:
    #     choice_data = df6[df6['products'].isin(choice)]  # Assuming df6 contains product-related data
    #     fig_0 = px.histogram(choice_data, x='products', y='counts', histfunc='count', color='airline_sentiment', facet_col='airline_sentiment', labels={'airline_sentiment':'tweets'}, height=600, width=800)
    #     st.plotly_chart(fig_0)


# with tab2:
  
#     # Read CSV data (replace with your actual path)
#     df = pd.read_csv('C:/Users/dell/OneDrive/Desktop/orders.csv')

#     # Assuming invalid times have a specific format (e.g., hours above 23)
#     # Assuming 'created_at' is a string column containing time values
#     valid_df = df[df['created_at'].apply(is_valid_time)]  # Apply validation function

#     # Optional: Assign filtered data to a new DataFrame
#     df = valid_df.copy()
#     # Handle invalid times using errors argument in to_datetime
#     df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')  # Replace invalid with NaT

#     # df_filtered = df[~df['created_at'].str.contains("30:")]  # Filter out rows with "30:" in time (optional)
#     # df = df_filtered.copy()  # Uncomment if you want to keep filtered data


#     # Assuming invalid times have a specific format (e.g., hours above 23)
#     # df_filtered = df[~df['created_at'].str.contains("30:")]  # Filter out rows with "30:" in time
#     # df = df_filtered.copy()  # Assign filtered data to a new DataFrame (optional)

#     # # Assuming you can adjust hours within a reasonable range (e.g., -12 to 12)
#     # df['created_at'] = pd.to_timedelta('09:00:00') + pd.to_timedelta(df['created_at'])  # Assuming invalid hours differ by a constant offset

#     # Handle invalid times using errors argument in to_datetime
#     # df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')  # Replace invalid with NaT

#     # Assuming 'created_at' is now (mostly) a datetime column
#     df['month'] = df['created_at'].dt.month_name()
#     month_names = df['month'].unique()  # Get unique month names for x-axis ticks

#     # Total received orders per month
#     total_received_per_month = df.groupby('month')['id'].count().reset_index()

#     # Completed orders per month
#     completed_df = df[df['status'] == 'COMPLETED']  # Assuming 'Completed' indicates completion
#     completed_per_month = completed_df.groupby('month')['id'].count().reset_index()

#     # Convert DataFrames to dictionaries for Streamlit plotting (alternative approach)
#     total_received_dict = total_received_per_month.set_index('month')['id'].to_dict()
#     completed_dict = completed_per_month.set_index('month')['id'].to_dict()

#     # Create charts (without plt.show())
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))  # Create a single figure with two subplots

#     # Total received orders plot
#     ax1.bar(total_received_per_month['month'], total_received_per_month['id'])
#     ax1.set_title('Total Received Orders')

#     # Completed orders plot
#     ax2.bar(completed_per_month['month'], completed_per_month['id'])
#     ax2.set_title('Completed Orders')

#     # Add trendline for total received orders
#     if total_received_dict and completed_dict:
#         # Check data types of dictionary values (assuming they might be strings or floats)
#         if any(not isinstance(v, (int, float)) for v in total_received_dict.values()):
#             st.warning("Total received order values contain non-numeric entries. Trendline omitted.")
#         else:
#             valid_months = [month for month in month_names if month in total_received_dict and month in completed_dict]
#             total_received_values = [total_received_dict.get(month, np.nan) for month in valid_months]
#             completed_values = [completed_dict.get(month, np.nan) for month in valid_months]  # Get completed values
#             slope, intercept, rvalue, _, _ = linregress(total_received_values, completed_values)
#             x = np.linspace(min(total_received_values), max(total_received_values))
#             y = slope * x + intercept
#             ax1.plot(x, y, color='red', linestyle='--')

#     # Add trendline for completed orders
#     if total_received_dict and completed_dict:
#         # Check data types of dictionary values (assuming they might be strings or floats)
#         if any(not isinstance(v, (int, float)) for v in completed_dict.values()):
#             st.warning("Completed order values contain non-numeric entries. Trendline omitted.")
#         else:
#             valid_months = [month for month in month_names if month in total_received_dict and month in completed_dict]
#             completed_values = list(completed_dict.values())
#             total_received_values = [total_received_dict.get(month, np.nan) for month in valid_months]  # Get total received values
#             slope, intercept, rvalue, _, _ = linregress(total_received_values, completed_values)
#             x = np.linspace(min(completed_values), max(completed_values))
#             y = slope * x + intercept
#             ax2.plot(x, y, color='blue', linestyle='--')

#     # Display plots in Streamlit
#     st.pyplot(fig)
# with tab3:
#     create_data_entry_form_and_return_csv()

    

