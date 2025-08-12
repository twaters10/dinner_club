
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import boto3
import io

# Define S3 Bucket and file key
BUCKET_NAME = "dinner-club-tsw"
FILE_KEY = "dinner_club_rankings.csv"

# Weights to each category
cols_to_display = ['Food Quality (0 - 10)',	
                    'Ambience (0 - 10)',
                    'Bathroom Quality (0 - 10)',
                    'Food Portion Size (0 - 10)',
                    'Service (0 - 10)',
                    'Drinks (0 - 10)']

# Initialize S3 Client
s3_client = boto3.client('s3')

# Create response object from S3
response = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)

# Read the content of the object
body = response['Body']
csv_string = body.read().decode('utf-8') # Decode bytes to string, assuming UTF-8
print(csv_string)

# --- Read the CSV using pandas from the string in memory ---
df = pd.read_csv(io.StringIO(csv_string))

# Get unique restaurants and respondents
restaurants = df['Restaurant'].unique()
respondents = df['Respondent Name'].unique()

# Streamlit app layout with sidebar
st.sidebar.header("Filters")

# Add selectbox for restaurant and respondent filters in the sidebar
selected_restaurant = st.sidebar.selectbox('Select Restaurant', ['All'] + list(restaurants))
selected_respondent = st.sidebar.selectbox('Select Respondent', ['All'] + list(respondents))

# Filter the DataFrame based on user selections
filtered_df = df.copy()  # Start with a copy of the original DataFrame

if selected_restaurant != 'All':
    filtered_df = filtered_df[filtered_df['Restaurant'] == selected_restaurant]

if selected_respondent != 'All':
    filtered_df = filtered_df[filtered_df['Respondent Name'] == selected_respondent]

# Categories for the spider plot
categories = cols_to_display

# Function to create spider plots for each restaurant
def create_spider_plot(df):
    fig = go.Figure()
    
    restaurants_to_plot = df['Restaurant'].unique()  # Use unique restaurants from the filtered DataFrame
    
    for restaurant in restaurants_to_plot:
        restaurant_df = df[df['Restaurant'] == restaurant]
        
        avg_scores = []
        for category in categories:
            if category in restaurant_df.columns:
                avg_scores.append(restaurant_df[category].mean())
            else:
                avg_scores.append(0)
        
        fig.add_trace(go.Scatterpolar(
            r=avg_scores,
            theta=categories,
            fill='toself',
            name=restaurant
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title='Restaurant Ranking Spider Plot'
    )
    return fig

# Main app content
st.title("Restaurant Ranking Spider Plot")

# Create and display the spider plot
fig = create_spider_plot(filtered_df)
st.plotly_chart(fig)

# Calculate average scores per category and overall weighted ranking
average_scores = filtered_df.groupby('Restaurant')[categories].mean()
average_weighted_ranking = filtered_df.groupby('Restaurant')['Weighted Ranking'].mean()
average_scores['Average Weighted Ranking'] = average_weighted_ranking

# Display the average scores in a table
st.subheader("Average Scores per Restaurant")
st.dataframe(average_scores)





