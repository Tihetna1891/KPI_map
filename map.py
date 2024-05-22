import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap, Fullscreen
import numpy as np
import altair as alt
import re
from folium.plugins import MarkerCluster

def convert_google_sheet_url(url):
    # Regular expression to match and capture the necessary part of the URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'
    new_url = re.sub(pattern, replacement, url)
    return new_url
def visualize_status_counts(df, selected_date_range):
    start_date, end_date = selected_date_range
    
    # Filter DataFrame for the selected date range
    filtered_data = df[(df['created_at'].dt.date >= start_date) & (df['created_at'].dt.date <= end_date)]
    
    # Calculate status counts
    status_counts = filtered_data['status'].value_counts().reset_index()
    status_counts['Percent'] = status_counts['count'] / status_counts['count'].sum() * 100
    
    st.markdown(f"### Status Counts for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    if status_counts.empty:
        st.markdown("No data available for the selected date range.")
    else:
        # Altair
        chart = alt.Chart(status_counts).mark_bar().encode(
            x='status',
            y='count',
            color='status',
            tooltip=['status', 'count', 'Percent']
        ).properties(
            title='Status Counts'
        )
        
        st.altair_chart(chart, use_container_width=True)  

def visualize_completion_time(df, selected_date_range):
    start_date, end_date = selected_date_range
    filtered_data = df[(df['created_at'].dt.date >= start_date) & 
                      (df['created_at'].dt.date <= end_date) & 
                      (df['status'] == 'COMPLETED')]
    
    if filtered_data.empty:
        st.markdown("No COMPLETED orders within the selected date range.")
        return

    completion_times = (filtered_data['updated_at'] - filtered_data['created_at']).dt.total_seconds() / 3600
    completion_times = completion_times.clip(lower=0, upper=48)
    # Create a DataFrame for visualization
    completion_df = pd.DataFrame({'Completion Time (hours)': completion_times})
    
    st.markdown(f"### Completed Groups from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    chart = alt.Chart(completion_df).mark_bar().encode(
        x=alt.X('Completion Time (hours)', bin=alt.Bin(step=1)),
        y='count()',
        tooltip=['count()']
    ).properties(
        title='Group Completion Time Distribution'
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)
# def visualize_tweets_on_map(df1,df, selected_date_range):
#     start_date, end_date = selected_date_range
    
#     # Filter DataFrame for tweets within the selected date range
#     filtered_data = df[(df['created_at'].dt.date >= start_date) & 
#                        (df['created_at'].dt.date <= end_date) &
#                        (df['status'] == 'COMPLETED')]
#     filtered_data = df1[df1['id'].isin(filtered_data['location_id'].unique())]
#     st.markdown("### Delivery tracks distribution based on the selected date range")
    
#     # if len(filtered_data) == 0:
#     #     st.markdown("No orders within the selected date range.")
#     # else:
#     #     st.markdown("%i orders from %s to %s" % (len(filtered_data), 
#     #                                               start_date.strftime('%Y-%m-%d'), 
#     #                                               end_date.strftime('%Y-%m-%d')))
#     if len(filtered_data) == 0:
#         st.markdown("No orders within the selected date range.")
#     else:
#         st.markdown("%i orders from %s to %s" % (len(filtered_data), 
#                                                   start_date.strftime('%Y-%m-%d'), 
#                                                   end_date.strftime('%Y-%m-%d')))
        
#         if len(filtered_data) > 0:
#             center_lat = filtered_data['latitude'].mean()
#             center_lon = filtered_data['longitude'].mean()
            
#             # Create a base map
#             m = folium.Map(location=[center_lat, center_lon], zoom_start=15)
            
#             # Prepare data for heatmap
#             heat_data = [[row['latitude'], row['longitude']] for index, row in filtered_data.iterrows() if not pd.isnull(row['latitude']) and not pd.isnull(row['longitude'])]
            
#             # Add heatmap layer to the map
#             HeatMap(heat_data).add_to(m)
            
#             # Display the map with Streamlit
#             full_size = st.checkbox("Full-size map")
#             height = 800 if full_size else 450
            
#             # Adjust map height based on the checkbox
#             folium_static(m, width=700, height=height)
#             # # Display the map with Streamlit
#             # folium_static(m)    
def visualize_tweets_on_map(filtered_data, selected_date_range):
    start_date, end_date = selected_date_range
    
     # Filter DataFrame for tweets within the selected date range
    filtered_data = filtered_data[(filtered_data['created_at'].dt.date >= start_date) & 
                       (filtered_data['created_at'].dt.date <= end_date) ]
    # filtered_data = df1[df1['id'].isin(filtered_data['location_id'].unique())]
    
    st.markdown("### Delivery locations distribution based on the selected date range")
    
    if len(filtered_data) == 0:
        st.markdown("No orders within the selected date range.")
    else:
        unique_locations = filtered_data[['latitude', 'longitude']].drop_duplicates()
        num_unique_locations = len(unique_locations)
        st.markdown("%i delivervy locations from %s to %s" % ((num_unique_locations), 
                                                  start_date.strftime('%Y-%m-%d'), 
                                                  end_date.strftime('%Y-%m-%d')))

        
        if len(filtered_data) > 0:
            center_lat = filtered_data['latitude'].mean()
            center_lon = filtered_data['longitude'].mean()
            
            # Create a base map
            m = folium.Map(location=[center_lat, center_lon], zoom_start=8)
            
            # Add clustering for better performance with large datasets
            marker_cluster = MarkerCluster().add_to(m)
            
            # Count completed orders at each location
            order_counts = filtered_data.groupby(['latitude', 'longitude']).size().reset_index(name='order_count')
            
            # Add markers for each location with popup displaying order count
            for index, row in order_counts.iterrows():
                folium.Marker(
                    location=(row['latitude'], row['longitude']),
                    popup=f"Completed Orders: {row['order_count']}"
                ).add_to(marker_cluster)
            
            # Display the map with Streamlit
            folium_static(m)   
def visualize_os_distribution(df, selected_date_range):
    start_date, end_date = selected_date_range
    
    # Filter DataFrame for orders within the selected date range
    filtered_data = df[(df['created_at'].dt.date >= start_date) & 
                       (df['created_at'].dt.date <= end_date)]
    
    if filtered_data.empty:
        st.markdown(f"No data available for the selected date range.")
        return
    
    # Count the occurrences of each OS
    os_counts = filtered_data['os'].value_counts().reset_index()
    os_counts.columns = ['OS', 'Count']
    
    # Create an Altair bar chart
    chart = alt.Chart(os_counts).mark_bar().encode(
        x='OS',
        y='Count',
        color=alt.Color('OS', scale=alt.Scale(range=['blue', 'green'])),
        tooltip=['OS', 'Count']
    ).properties(
        title=f'OS Distribution from {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'
    ).interactive()
    
    # Display the chart
    st.altair_chart(chart, use_container_width=True)
def visualize_max_group_member(df0, df1, df2, df3, selected_date_range):
    start_date, end_date = selected_date_range
    
    # Filter DataFrame df0 for completed orders within the selected date range
    filtered_df0 = df0[(df0['created_at'].dt.date >= start_date) & 
                       (df0['created_at'].dt.date <= end_date) & 
                       (df0['status'] == 'COMPLETED')]
    
    if filtered_df0.empty:
        st.markdown("### No data available for the selected date range and status in df0")
        return
 
    # Filter DataFrame df1 with ids from filtered_df0
    filtered_df1 = df1[df1['id'].isin(filtered_df0['groups_carts_id'])]
    
    if filtered_df1.empty:
        st.markdown("### No data available in df1 after filtering with df0")
        return
    
    # Filter DataFrame df2 with ids from filtered_df1
    filtered_df2 = df2[df2['id'].isin(filtered_df1['group_id'])]
    
    if filtered_df2.empty:
        st.markdown("### No data available in df2 after filtering with df1")
        return
    
    # Filter DataFrame df3 with ids from filtered_df2
    filtered_df3 = df3[df3['id'].isin(filtered_df2['group_deals_id'])]
    
    if filtered_df3.empty:
        st.markdown("### No data available in df3 after filtering with df2")
        return
    
    # Count the occurrences of max_group_member
    counts = filtered_df3['max_group_member'].value_counts().reset_index()
    counts.columns = ['Max Group Member', 'Count']
    
    # Round max_group_member values to integers
    counts['Max Group Member'] = counts['Max Group Member'].astype(int)
    
    # Create an Altair bar chart
    chart = alt.Chart(counts).mark_bar().encode(
        x=alt.X('Max Group Member', title='Max Group Member'),
        y=alt.Y('Count', title='Count'),
        tooltip=['Max Group Member', 'Count']
    ).properties(
        title='Max Group Member Counts'
    ).interactive()
    st.altair_chart(chart, use_container_width=True)
def count_refund_status(df, selected_date_range):
    start_date, end_date = selected_date_range
    filtered_df = df[(df['created_at'].dt.date >= start_date) & 
                     (df['created_at'].dt.date <= end_date)]
    if filtered_df.empty:
        st.markdown("### No data available for the selected date range")
        return
    status_counts = filtered_df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    chart = alt.Chart(status_counts).mark_bar().encode(
        x='Status',
        y='Count',
        color='Status'
    ).properties(
        title='Status Counts',
        width=500,
        height=300
    ).interactive()
    st.altair_chart(chart, use_container_width=True)
def create_data_entry_form_and_return_csv():
    with st.form(key='data_entry_form'):
        st.write("Inside the form")
        url = convert_google_sheet_url('https://docs.google.com/spreadsheets/d/1QJi3WJoBHQ9X92ezeTE8WHZM3gCQMJweOXmLmcw-phA/edit?usp=sharing')
        survey = pd.read_csv(url)
        col1, col2 = st.columns(2)
        options = col1.selectbox("select product",tuple(survey['Products List'].unique()))
        date_input = col2.date_input(label='Enter a date')
        st.write("insert price for each benchmarks")
        number_inputs = {}
        for i in survey['Location'].unique():
            number_inputs[i]=st.number_input(label = f'{i}')
        submitted = st.form_submit_button('Submit')
        if submitted:
            form_data = {
                'Text': [text_input],
                'Number': [number_input],
                'Date': [date_input],
                'Time': [time_input]
            }
            df = pd.DataFrame(form_data)
            csv = df.to_csv(index=False)
            csv_buffer = StringIO(csv)
            st.download_button(
                label="Download data as CSV",
                data=csv_buffer,
                file_name='form_data.csv',
                mime='text/csv'
            )
