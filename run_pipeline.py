from Steps.ingest_data import *
from Steps.data_prep import *
from Steps.load_to_s3 import *

if __name__ == "__main__":
    df = ingest_data(google_sheets_json_path = '/Users/tawate/Documents/Dinner Club/clean-terminal-468616-k8-06169f567f7e.json', 
                     spreadsheet_title = "Dinner Club Ranking (Responses)")
    
    # Apply Weights to each category
    restaurant_rankings = {
        'Food Quality (0 - 10)': {
            'weight': 0.5
        },
        'Food Portion Size (0 - 10)': {
            'weight': 0.1
        },
        'Drinks (0 - 10)': {
            'weight': 0.1
        },
        'Service (0 - 10)': {
            'weight': 0.1
        },
        'Ambience (0 - 10)': {
            'weight': 0.1
        },
        'Bathroom Quality (0 - 10)': {
            'weight': 0.1
        }
    } 

    # Convert relevant columns to numeric, handling potential errors
    cols_to_convert = ['Food Quality (0 - 10)',	
                       'Ambience (0 - 10)',
                       'Bathroom Quality (0 - 10)',
                       'Food Portion Size (0 - 10)',
                       'Service (0 - 10)',
                       'Drinks (0 - 10)']
    
    # Prep data
    prepare_data(df, cols_to_convert)
    
    # Function to calculate weighted ranking
    def calculate_weighted_ranking(row):
        """ Calculates the weighted ranking for a given row based on the restaurant rankings.
        Args:
            row (pd.Series): A row from the DataFrame containing restaurant ratings.
            restaurant_rankings (dict): A dictionary containing the weights for each category.
        Returns:
            float: The weighted sum of the ratings for the restaurant.
        """
        weighted_sum = 0
        for category, details in restaurant_rankings.items():
            if category in row.index:  # Check if the category exists in the row
                weighted_sum += row[category] * details['weight']
        return weighted_sum   
    
    # Apply the function to each row to create a 'Weighted Ranking' column
    df['Weighted Ranking'] = df.apply(calculate_weighted_ranking, axis=1)

    # Load processed data to S3
    load_processed_data_to_s3(df, bucket_name = 'dinner-club-tsw', csvfilename = 'dinner_club_rankings.csv')