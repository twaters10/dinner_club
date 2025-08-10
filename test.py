import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# Step 1: Authenticate with Google Sheets
# Define the scope and path to your service account key file
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/tawate/Documents/Dinner Club/clean-terminal-468616-k8-06169f567f7e.json', scope)
client = gspread.authorize(creds)

# Step 2: Open the spreadsheet
# You can open it by title, key, or URL
try:
    # Open by title
    sheet = client.open("Dinner Club Ranking (Responses)").sheet1  # Use .sheet1 for the first worksheet

    # Or, open by spreadsheet key (the long string in the URL)
    # sheet = client.open_by_key("your-spreadsheet-key").sheet1

    # Or, open by URL
    # sheet_url = "https://docs.google.com/spreadsheets/d/your-spreadsheet-key/edit"
    # sheet = client.open_by_url(sheet_url).sheet1

except gspread.exceptions.SpreadsheetNotFound:
    print("Spreadsheet not found. Please check the title and sharing permissions.")
    exit()

# Step 3: Get all the data from the worksheet
data = sheet.get_all_values()

# Step 4: Convert the data into a pandas DataFrame
# The first row is typically the header
headers = data[0]
df = pd.DataFrame(data[1:], columns=headers)

# Display the DataFrame
print(df.head())

# You can now work with the pandas DataFrame as you normally would
# For example, to print a specific column:
# print(df['Column Name'])

# Apply Weights to each category
restaurant_rankings = {
    'Food Taste': {
        'weight': 0.5
    },
    'Food Portion Size': {
        'weight': 0.1
    },
    'Drinks': {
        'weight': 0.1
    },
    'Service': {
        'weight': 0.1
    },
    'Ambiance': {
        'weight': 0.1
    },
    'Bathroom': {
        'weight': 0.1
    }
} 

# The sum of all weights should ideally be 1.0. Let's check:
total_weight = sum(category['weight'] for category in restaurant_rankings.values())
print(f"Total weight of all categories: {total_weight}\n")

# Standardize the column names in the DataFrame to match the keys in restaurant_rankings
df.rename(columns={
    'Food Quality': 'Food Taste',
    'Ambience ': 'Ambiance',
    'Bathroom Quality': 'Bathroom',
    'Food Portion Size (10 = Large, 1 = Small)': 'Food Portion Size',
    'Service': 'Service',
    'Drinks': 'Drinks'
}, inplace=True)

# Convert relevant columns to numeric, handling potential errors
cols_to_convert = ['Food Taste', 'Food Portion Size', 'Service', 'Ambiance', 'Bathroom', 'Drinks']
for col in cols_to_convert:
    df[col] = pd.to_numeric(df[col], errors='coerce')  # 'coerce' will turn invalid parsing into NaN

# Function to calculate weighted ranking
def calculate_weighted_ranking(row):
    weighted_sum = 0
    for category, details in restaurant_rankings.items():
        if category in row.index:  # Check if the category exists in the row
            weighted_sum += row[category] * details['weight']
    return weighted_sum

# Apply the function to each row to create a 'Weighted Ranking' column
df['Weighted Ranking'] = df.apply(calculate_weighted_ranking, axis=1)

# Print the DataFrame with the new 'Weighted Ranking' column
print(df[['Restaurant', 'Food Taste', 'Food Portion Size', 'Drinks', 'Service', 'Ambiance', 'Bathroom', 'Weighted Ranking']].head())

# Calculate average Weighted Ranking by Restaurant
average_rankings = df.groupby('Restaurant')['Weighted Ranking'].mean().sort_values(ascending=False)

# Print the average rankings
print("Average Weighted Ranking by Restaurant:\n", average_rankings)


# Calculate average scores for each category per restaurant
average_scores = df.groupby('Restaurant')[['Food Taste', 'Food Portion Size', 'Drinks', 'Service', 'Ambiance', 'Bathroom']].mean()

# Calculate average weighted ranking per restaurant (already done in CELL INDEX 3, but included here for completeness)
average_weighted_ranking = df.groupby('Restaurant')['Weighted Ranking'].mean()

# Add the average weighted ranking to the average_scores DataFrame
average_scores['Average Weighted Ranking'] = average_weighted_ranking

# Print the average scores
print("Average Scores per Restaurant:\n", average_scores)


import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Assuming df and restaurant_rankings are already defined as in previous cells

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
categories = list(restaurant_rankings.keys())

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

