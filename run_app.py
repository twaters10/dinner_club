
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import s3fs

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

# Use st.secrets to access your AWS credentials
try:
    aws_access_key_id = st.secrets["aws"]["aws_access_key_id"]
    aws_secret_access_key = st.secrets["aws"]["aws_secret_access_key"]
except KeyError:
    st.error("AWS credentials not found in secrets.toml. Please configure them.")
    st.stop()

# Create an S3 filesystem object using the retrieved credentials
# s3fs handles the authentication for you
s3 = s3fs.S3FileSystem(key=aws_access_key_id, secret=aws_secret_access_key)

try:
    # Construct the full S3 path
    s3_path = f"s3://{BUCKET_NAME}/{FILE_KEY}"
    
    # Use pandas to read the CSV file directly from S3
    # The 'storage_options' argument is used to pass the credentials to pandas
    df = pd.read_csv(s3_path, storage_options=s3.storage_options)

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.info("Please double-check your S3 bucket name, file key, and AWS permissions.")

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

# Create a bar chart with average weighted rankings sort from highest to lowest by restaurant
st.subheader("Average Weighted Rankings")
bar_fig = go.Figure()
sorted_rankings = average_weighted_ranking.sort_values(ascending=False)
bar_fig.add_trace(go.Bar(
    x=sorted_rankings.index,
    y=sorted_rankings.values,
    marker_color='indianred'
))
bar_fig.update_layout(
    title='Average Weighted Rankings by Restaurant',
    xaxis_title='Restaurant',
    yaxis_title='Average Weighted Ranking',
    yaxis=dict(range=[0, 10])
)
st.plotly_chart(bar_fig)
# Display raw data if checkbox is selected
if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data")
    st.dataframe(filtered_df)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='filtered_restaurant_rankings.csv',
        mime='text/csv',
    )
# Footer
st.markdown("""
---
*Developed by Your Taylor Waters*
""")





