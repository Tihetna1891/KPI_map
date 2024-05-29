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
@st.cache_data
def convert_google_sheet_url(url):
    # Regular expression to match and capture the necessary part of the URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'
    new_url = re.sub(pattern, replacement, url)
    return new_url
@st.cache_data
def calculate_time_frame(df, selected_date_range, selected_time_frame):
    """
    Calculate the time frame column based on the selected time frame.

    Args:
        df: DataFrame containing the data.
        selected_date_range: Tuple containing the start and end dates of the selected date range.
        selected_time_frame: String representing the selected time frame ('daily', 'weekly', 'monthly', 'yearly').

    Returns:
        DataFrame with the 'time_frame' column added.
    """
    start_date, end_date = selected_date_range

    if selected_time_frame == 'daily':
        df['time_frame'] = df['created_at'].dt.date
    elif selected_time_frame == 'weekly':
        df['time_frame'] = df['created_at'].dt.to_period('W').apply(lambda r: r.start_time)
    elif selected_time_frame == 'monthly':
        df['time_frame'] = df['created_at'].dt.to_period('M').apply(lambda r: r.start_time)
    elif selected_time_frame == 'yearly':
        df['time_frame'] = df['created_at'].dt.to_period('Y').apply(lambda r: r.start_time)
    else:
        raise ValueError("Invalid time frame. Choose from 'daily', 'weekly', 'monthly', or 'yearly'.")

    # Filter DataFrame based on selected date range
    df = df[(df['created_at'] >= start_date) & (df['created_at'] <= end_date)]

    return df
       


@st.cache_data
def calculate_time_frame(df, selected_date_range, time_frame):
    """
    Calculate the time frame column based on the selected date range and time frame.

    Args:
        df: DataFrame containing the data.
        selected_date_range: Tuple containing the start and end date of the selected date range.
        time_frame: Selected time frame ('daily', 'weekly', 'monthly', or 'yearly').

    Returns:
        DataFrame with the 'time_frame' column added.
    """
    # Copy the DataFrame to avoid modifying the original DataFrame
    df = df.copy()

    # Extract start and end dates from the selected date range
    start_date, end_date = selected_date_range

    # Create a mask to filter data within the selected date range
    # mask = (df['created_at'] >= start_date) & (df['created_at'] <= end_date)
    mask = (df['created_at'].dt.date >= start_date) &  (df['created_at'].dt.date <= end_date)

    # Apply the mask to filter data
    df = df[mask]

    # Calculate the time frame column based on the selected time frame
    if time_frame == 'daily':
        df['time_frame'] = df['created_at'].dt.date
    elif time_frame == 'weekly':
        df['time_frame'] = df['created_at'].dt.to_period('W').apply(lambda r: r.start_time)
    elif time_frame == 'monthly':
        df['time_frame'] = df['created_at'].dt.to_period('M').apply(lambda r: r.start_time)
    elif time_frame == 'yearly':
        df['time_frame'] = df['created_at'].dt.to_period('Y').apply(lambda r: r.start_time)
    else:
        raise ValueError("Invalid time frame. Choose from 'daily', 'weekly', 'monthly', or 'yearly'.")

    return df
  

# visualize status count with time frames
@st.cache_data
def visualize_status_counts_timeframe(df, selected_date_range, time_frame):
    # start_date, end_date = selected_date_range
    df = calculate_time_frame(df, selected_date_range, time_frame)
    # Filter DataFrame for the selected date range
    # filtered_data = df[(df['created_at'].dt.date >= start_date) & (df['created_at'].dt.date <= end_date)]
    
    # Resample data according to the selected time frame
    # if time_frame == 'daily':
    #     df['time_frame'] = df['created_at'].dt.date
    # elif time_frame == 'weekly':
    #     df['time_frame'] = df['created_at'].dt.to_period('W').apply(lambda r: r.start_time)
    # elif time_frame == 'monthly':
    #     df['time_frame'] = df['created_at'].dt.to_period('M').apply(lambda r: r.start_time)
    # elif time_frame == 'yearly':
    #     df['time_frame'] = df['created_at'].dt.to_period('Y').apply(lambda r: r.start_time)
    # else:
    #     raise ValueError("Invalid time frame. Choose from 'daily', 'weekly', 'monthly', or 'yearly'.")
  

    # Calculate status counts
    status_counts = df.groupby(['time_frame', 'status']).size().reset_index(name='count')
    status_counts['Percent'] = status_counts['count'] / status_counts.groupby('time_frame')['count'].transform('sum') * 100
    
    # st.markdown(f"### Order Status Counts from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    st.markdown(f"### Order Status Counts {time_frame} report")
    if status_counts.empty:
        st.markdown("No data available for the selected date range.")
    else:
        # Altair
        chart = alt.Chart(status_counts).mark_bar().encode(
            x='time_frame:T',
            y='count',
            color='status',
            tooltip=['status', 'count', 'Percent']
        ).properties(
            title='Status Counts'
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
@st.cache_data
def visualize_completion_time(df, selected_date_range):
    start_date, end_date = selected_date_range
    # filtered_data = df[(df['created_at'].dt.date >= start_date) & 
    #                   (df['created_at'].dt.date <= end_date) & 
    #                   (df['status'] == 'COMPLETED')]
    df = df[(df['created_at'].dt.date >= start_date) & (df['created_at'].dt.date <= end_date)]
    
    if df.empty:
        st.markdown("No COMPLETED orders within the selected date range.")
        return

    completion_times = (df['updated_at'] - df['created_at']).dt.total_seconds() / 3600
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

# visualize completion_time with time frame
@st.cache_data
def visualize_completion_time_timeframe(df, selected_date_range, time_frame):
    # start_date, end_date = selected_date_range
    df = calculate_time_frame(df, selected_date_range, time_frame)
    # Filter DataFrame for the selected date range
    # filtered_data = df[(df['created_at'].dt.date >= start_date) & 
    #                   (df['created_at'].dt.date <= end_date) & 
    #                   (df['status'] == 'COMPLETED')]
    # df = df[(df['created_at'].dt.date >= start_date) & 
    #                 (df['created_at'].dt.date <= end_date)]

    if df.empty:
       st.markdown("No COMPLETED orders within the selected date range.")
       return

    
    # # Resample data according to the selected time frame
    # if time_frame == 'daily':
    #     df['time_frame'] = df['created_at'].dt.date
    # elif time_frame == 'weekly':
    #     df['time_frame'] = df['created_at'].dt.to_period('W').apply(lambda r: r.start_time)
    # elif time_frame == 'monthly':
    #     df['time_frame'] = df['created_at'].dt.to_period('M').apply(lambda r: r.start_time)
    # elif time_frame == 'yearly':
    #     df['time_frame'] = df['created_at'].dt.to_period('Y').apply(lambda r: r.start_time)
    # else:
    #     raise ValueError("Invalid time frame. Choose from 'daily', 'weekly', 'monthly', or 'yearly'.")
    
    completion_times = (df['updated_at'] - df['created_at']).dt.total_seconds() / 3600
    completion_times = completion_times.clip(lower=0, upper=24)
    # Create a DataFrame for visualization
    completion_df = pd.DataFrame({
        'Completion Time (hours)': completion_times,
        'time_frame': df['time_frame']
    })
    
    # st.markdown(f"### Completed Groups from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    st.markdown(f"### Completed Groups {time_frame} report")
    # unique_time_frames = df['time_frame'].unique()
    # st.write("Unique Time Frames:", unique_time_frames)  # Print unique time frames for debugging
    
    # Define a color scale for different time frames
    # color_scale = alt.Scale(domain=list(unique_time_frames), range=['red', 'green', 'blue', 'orange', 'yellow'])

    # color_scale = alt.Scale(domain=df['time_frame'].unique(), range=['red', 'green', 'blue', 'orange', 'yellow'])
    chart = alt.Chart(completion_df).mark_bar().encode(
        x=alt.X('Completion Time (hours)', bin=alt.Bin(step=1)),
        y='count()',
        color='time_frame',#alt.Color('time_frame', scale=color_scale),
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
@st.cache_data  
def visualize_tweets_on_map(filtered_data, selected_date_range):
    start_date, end_date = selected_date_range
    

    # Filter DataFrame for tweets within the selected date range
    filtered_data = filtered_data[(filtered_data['created_at'].dt.date >= start_date) & (filtered_data['created_at'].dt.date <= end_date)]

     # Filter DataFrame for tweets within the selected date range
    filtered_data = filtered_data[(filtered_data['created_at'].dt.date >= start_date) & 
                       (filtered_data['created_at'].dt.date <= end_date) ]

    # filtered_data = df1[df1['id'].isin(filtered_data['location_id'].unique())]
    
    st.markdown("### Delivery locations distribution based on the selected date range")
    
    if len(filtered_data) == 0:
        st.markdown("No orders within the selected date range.")
    else:

        # Count unique delivery locations
        unique_locations = filtered_data[['latitude', 'longitude']].drop_duplicates()
        num_unique_locations = len(unique_locations)
        st.markdown("%i delivervy locations from %s to %s" % ((num_unique_locations), start_date.strftime('%Y-%m-%d'),end_date.strftime('%Y-%m-%d')))        

        unique_locations = filtered_data[['latitude', 'longitude']].drop_duplicates()
        num_unique_locations = len(unique_locations)
        st.markdown("%i delivervy locations from %s to %s" % ((num_unique_locations), 
                                                  start_date.strftime('%Y-%m-%d'), 
                                                  end_date.strftime('%Y-%m-%d')))

        
        if len(filtered_data) > 0:
            center_lat = filtered_data['latitude'].mean()
            center_lon = filtered_data['longitude'].mean()
            
            # Create a base map
            m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
            
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
def visualize_tweets_on_map_timeframe(filtered_data, selected_date_range,time_frame):
    # start_date, end_date = selected_date_range
    filtered_data = calculate_time_frame(filtered_data, selected_date_range, time_frame)
    
    # Filter DataFrame for tweets within the selected date range
    # filtered_data = filtered_data[(filtered_data['created_at'].dt.date >= start_date) & 
    #                    (filtered_data['created_at'].dt.date <= end_date)]
    # filtered_data = df1[df1['id'].isin(filtered_data['location_id'].unique())]
    
    # st.markdown("### Delivery locations distribution based on the selected date range")
    st.markdown(f"### Delivery locations distribution  {time_frame} report")
    
    if len(filtered_data) == 0:
        st.markdown("No orders within the selected date range.")
    else:
        # Count unique delivery locations
        unique_locations = filtered_data[['latitude', 'longitude']].drop_duplicates()
        num_unique_locations = len(unique_locations)
        st.markdown("%i delivery locations %s" % (num_unique_locations, time_frame))

        
        if len(filtered_data) > 0:
            center_lat = filtered_data['latitude'].mean()
            center_lon = filtered_data['longitude'].mean()
            
            # Create a base map
            m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
            
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
# @st.cache_data 
# def visualize_os_distribution(df, selected_date_range):
#     start_date, end_date = selected_date_range
    
#     # Filter DataFrame for orders within the selected date range
#     # filtered_data = df[(df['created_at'].dt.date >= start_date) & 
#     #                    (df['created_at'].dt.date <= end_date)]
    
#     if df.empty:
#         st.markdown(f"No data available for the selected date range.")
#         return
    
#     # Count the occurrences of each OS
#     os_counts = df['os'].value_counts().reset_index()
#     os_counts.columns = ['OS', 'Count']
    
#     # Create an Altair bar chart
#     chart = alt.Chart(os_counts).mark_bar().encode(
#         x='OS',
#         y='Count',
#         color=alt.Color('OS', scale=alt.Scale(range=['blue', 'green'])),
#         tooltip=['OS', 'Count']
#     ).properties(
#         title=f'OS Distribution from {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'
#     ).interactive()
    
#     # Display the chart
#     st.altair_chart(chart, use_container_width=True)

# #visualize os distribution with time frame
# @st.cache_data
# def visualize_os_distribution_timeframe(df, selected_date_range, time_frame):
#     start_date, end_date = selected_date_range
    
#     # Filter DataFrame for orders within the selected date range
#     # filtered_data = df[(df['created_at'].dt.date >= start_date) & 
#     #                    (df['created_at'].dt.date <= end_date)]
    
#     if df.empty:
#         st.markdown(f"No data available for the selected date range.")
#         return
    
#     # Resample data according to the selected time frame
#     if time_frame == 'daily':
#         df['time_frame'] = df['created_at'].dt.date
#     elif time_frame == 'weekly':
#         df['time_frame'] = df['created_at'].dt.to_period('W').apply(lambda r: r.start_time)
#     elif time_frame == 'monthly':
#         df['time_frame'] = df['created_at'].dt.to_period('M').apply(lambda r: r.start_time)
#     elif time_frame == 'yearly':
#         df['time_frame'] = df['created_at'].dt.to_period('Y').apply(lambda r: r.start_time)
#     else:
#         raise ValueError("Invalid time frame. Choose from 'daily', 'weekly', 'monthly', or 'yearly'.")
    
#     # Count the occurrences of each OS
#     os_counts = df.groupby(['time_frame', 'os']).size().reset_index(name='Count')
    
#     # Create an Altair bar chart
#     chart = alt.Chart(os_counts).mark_bar().encode(
#         x='time_frame:T',
#         y='Count',
#         color='os',
#         tooltip=['time_frame:T', 'os', 'Count']
#     ).properties(
#         title=f'OS Distribution from {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'
#     ).interactive()
    
#     # Display the chart
#     st.altair_chart(chart, use_container_width=True)
@st.cache_data   
def visualize_max_group_member(df, selected_date_range):
    start_date, end_date = selected_date_range
    
    # Filter DataFrame df0 for completed orders within the selected date range
    # filtered_df0 = df0[(df0['created_at'].dt.date >= start_date) & 
    #                    (df0['created_at'].dt.date <= end_date) & 
    #                    (df0['status'] == 'COMPLETED')]
    df = df[(df['created_at'].dt.date >= start_date) & 
                (df['created_at'].dt.date <= end_date)]
    if df.empty:
        st.markdown("### No data available for the selected date range and status in df0")
        return
 
    # Filter DataFrame df1 with ids from filtered_df0
    # filtered_df1 = df1[df1['id'].isin(filtered_df0['groups_carts_id'])]
    
    # if filtered_df1.empty:
    #     st.markdown("### No data available in df1 after filtering with df0")
    #     return
    
    # Filter DataFrame df2 with ids from filtered_df1
    # filtered_df2 = df2[df2['id'].isin(filtered_df1['group_id'])]
    
    # if filtered_df2.empty:
    #     st.markdown("### No data available in df2 after filtering with df1")
    #     return
    
    # # Filter DataFrame df3 with ids from filtered_df2
    # filtered_df3 = df3[df3['id'].isin(filtered_df2['group_deals_id'])]
    
    # if filtered_df3.empty:
    #     st.markdown("### No data available in df3 after filtering with df2")
    #     return
    
    # Count the occurrences of max_group_member
    counts = df['max_group_member'].value_counts().reset_index()
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

# visualize max group with time frame 
@st.cache_data
def visualize_max_group_member_timeframe(df,selected_date_range, time_frame):
    # start_date, end_date = selected_date_range
    df = calculate_time_frame(df, selected_date_range, time_frame)
    
    # Filter DataFrame df0 for completed orders within the selected date range
    # filtered_df0 = df0[(df0['created_at'].dt.date >= start_date) & 
    #                    (df0['created_at'].dt.date <= end_date) & 
    #                    (df0['status'] == 'COMPLETED')]
    # df = df[(df['created_at'].dt.date >= start_date) & 
    #             (df['created_at'].dt.date <= end_date)]
    if df.empty:
        st.markdown("### No data available for the selected date range and status in df0")
        return
 
    # Filter DataFrame df1 with ids from filtered_df0
    # filtered_df1 = df1[df1['id'].isin(filtered_df0['groups_carts_id'])]
    
    # if filtered_df1.empty:
    #     st.markdown("### No data available in df1 after filtering with df0")
    #     return
    
    # Filter DataFrame df2 with ids from filtered_df1
    # filtered_df2 = df2[df2['id'].isin(filtered_df1['group_id'])]
    
    # if filtered_df2.empty:
    #     st.markdown("### No data available in df2 after filtering with df1")
    #     return
    
    # Filter DataFrame df3 with ids from filtered_df2
    # filtered_df3 = df3[df3['id'].isin(filtered_df2['group_deals_id'])]
    
    # if filtered_df3.empty:
    #     st.markdown("### No data available in df3 after filtering with df2")
    #     return
    
    # Resample data according to the selected time frame
    # if time_frame == 'daily':
    #     df['time_frame'] = df['created_at'].dt.date
    # elif time_frame == 'weekly':
    #     df['time_frame'] = df['created_at'].dt.to_period('W').apply(lambda r: r.start_time)
    # elif time_frame == 'monthly':
    #     df['time_frame'] = df['created_at'].dt.to_period('M').apply(lambda r: r.start_time)
    # elif time_frame == 'yearly':
    #     df['time_frame'] = df['created_at'].dt.to_period('Y').apply(lambda r: r.start_time)
    # else:
    #     raise ValueError("Invalid time frame. Choose from 'daily', 'weekly', 'monthly', or 'yearly'.")

    # Count the occurrences of max_group_member
    
    counts = df.groupby(['time_frame', 'max_group_member']).size().reset_index(name='Count')
    counts['max_group_member'] = counts['max_group_member'].astype(int)
    st.markdown(f"### the occurrences of max_group_member {time_frame} report")
    # Create an Altair bar chart
    chart = alt.Chart(counts).mark_bar().encode(
        x=alt.X('max_group_member:O', title='Max Group Member'),
        y=alt.Y('Count:Q', title='Count'),
        color='time_frame:T',
        tooltip=['time_frame:T', 'max_group_member:O', 'Count:Q']
    ).properties(
        title='Max Group Member Counts'
    ).interactive()
    st.altair_chart(chart, use_container_width=True)
@st.cache_data
def count_refund_status(df, selected_date_range):
    start_date, end_date = selected_date_range
    # filtered_df = df[(df['created_at'].dt.date >= start_date) & 
    #                  (df['created_at'].dt.date <= end_date)]
    df = df[(df['created_at'].dt.date >= start_date) & 
                (df['created_at'].dt.date <= end_date)]
    if df.empty:
        st.markdown("### No data available for the selected date range")
        return
    status_counts = df['status'].value_counts().reset_index()
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

@st.cache_data
def count_refund_status_timeframe(df, selected_date_range, time_frame):
    # start_date, end_date = selected_date_range
    df = calculate_time_frame(df, selected_date_range, time_frame)
    # filtered_df = df[(df['created_at'].dt.date >= start_date) & 
    #                  (df['created_at'].dt.date <= end_date)]
    # df = df[(df['created_at'].dt.date >= start_date) & 
    #             (df['created_at'].dt.date <= end_date)]
    if df.empty:
        st.markdown("### No data available for the selected date range")
        return
    
    # Resample data according to the selected time frame
    # if time_frame == 'daily':
    #     df['time_frame'] = df['created_at'].dt.date
    # elif time_frame == 'weekly':
    #     df['time_frame'] = df['created_at'].dt.to_period('W').apply(lambda r: r.start_time)
    # elif time_frame == 'monthly':
    #     df['time_frame'] = df['created_at'].dt.to_period('M').apply(lambda r: r.start_time)
    # elif time_frame == 'yearly':
    #     df['time_frame'] = df['created_at'].dt.to_period('Y').apply(lambda r: r.start_time)
    # else:
    #     raise ValueError("Invalid time frame. Choose from 'daily', 'weekly', 'monthly', or 'yearly'.")

    # Count the occurrences of refund status by time frame
    status_counts = df.groupby(['time_frame', 'status']).size().reset_index(name='Count')
    st.markdown(f"### occurrences of refund status {time_frame} report")
    # Create an Altair bar chart
    chart = alt.Chart(status_counts).mark_bar().encode(
        x=alt.X('time_frame:T', title='Time Frame'),
        y=alt.Y('Count:Q', title='Count'),
        color='status:N',
        tooltip=['time_frame:T', 'status:N', 'Count:Q']
    ).properties(
        title='Status Counts Over Time',
        width=700,
        height=400
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
