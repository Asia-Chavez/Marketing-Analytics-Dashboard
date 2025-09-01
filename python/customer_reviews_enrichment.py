# pip install pandas nltk pyodbc sqlalchemy

import pandas as pd
import pyodbc
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import Counter
import re # for splitting words more robustly
from datetime import datetime

# Download the VADER lexicon for sentiment analysis if not already present
nltk.download('vader_lexicon')

# Define a function to fetch data from a SQL database using a SQL qyery
def fetch_data_from_sql():
    # Define the connection string with parameters for the database connection
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};" # Specify the driver for SQL Server
        "Server=LAPTOP-2L66TUUK\SQLEXPRESS;" # Specify your SQL Server instance
        "Database=PortfolioProject_MarketingAnalytics;" # Specify the database name
        "Trusted_Connection=yes;" # Use Windows Authentication for the connection
    )
    # Establish the connection to the database
    conn = pyodbc.connect(conn_str)

    # Define the SQL query to fetch customer reviews data
    query = "SELECT ReviewID, CustomerID, ProductID, ReviewDate, Rating, ReviewText FROM customer_reviews"
    
    # Execute the query and fetch the data into a DataFrame
    df = pd.read_sql(query, conn)
    df['ReviewText'] = df['ReviewText'].str.replace(r'\s+', ' ', regex=True)
    print(df.head())

    # Close the connection to free up resources
    conn.close()

    # Return the fetched data as a DataFrame
    return df

# Fetch the customer reviews data from the SQL database
customer_reviews_df = fetch_data_from_sql()

# Initialize the VADER sentiment intensity analyzer for analyzing the sentiment of text data
sia = SentimentIntensityAnalyzer()

# Define a function to calculate sentiment scores using VADER
def calculate_sentiment(review):
    # Get the sentiment scores for the review text
    sentiment = sia.polarity_scores(review)
    # Return the compound score which is a normalized score between -1 (most negative) and 1 (most positive)
    return sentiment['compound']

# Define a function to categorize sentiment using both the sentiment score and the review rating
def categorize_sentiment(score, rating):
    # Use both the text sentiment score and the numerical rating to determine sentiment category
    if score > 0.05: # Positive sentiment score
        if rating >=4:
            return 'Positive' # High rating, positive sentiment
        elif rating == 3:
            return 'Mixed Positive' # Neutral rating, positive sentiment
        else:
            return 'Mixed Negative' # Low rating, positive sentiment        
    elif score < -0.05: # Negative sentiment score
        if rating <=2:
            return 'Negative' # Low rating, negative sentiment
        elif rating == 3:
            return 'Mixed Negative' # Neutral rating, negative sentiment
        else:
            return 'Mixed Positive' # High rating, negative sentiment
    else: # Neutral sentiment score
        if rating >=4:
            return 'Positive' # High rating, neutral sentiment
        elif rating <=2:
            return 'Negative' # Low rating, neutral sentiment
        else:
            return 'Neutral' # Neutral rating, neutral sentiment

# Define a function to bucket sentiment scores into text ranges
def sentiment_bucket(score):
    if score >= 0.5:
        return 'Positive' # Strongly positive sentiment
    elif 0.0 <= score < 0.5:
        return 'Mildy Positive' # Mildly positive sentiment
    elif -0.5 <= score < 0.0:
        return 'Mildly Negative' # Mildly negative sentiment
    else:
        return 'Negative' # Strongly negative sentiment

# Apply sentiment analysis to calculate sentiment scores for each review
customer_reviews_df['SentimentScore'] = customer_reviews_df['ReviewText'].apply(calculate_sentiment)

# Apply sentiment categorization using both text and rating
customer_reviews_df['SentimentCategory'] = customer_reviews_df.apply(
    lambda row: categorize_sentiment(row['SentimentScore'], row['Rating']), axis=1)

# Apply sentiment bucketing to categorize scores into defined ranges
customer_reviews_df['SentimentBucket'] = customer_reviews_df['SentimentScore'].apply(sentiment_bucket)

# Determine top common reviews
common_reviews = customer_reviews_df['ReviewText'].value_counts()
# Convert output to DataFrame
common_reviews_df = common_reviews.reset_index()
common_reviews_df.columns = ['CommonReviews', 'Count'] # Rename columns for clarity
# Add average rating column per common review
average_ratings_by_review = customer_reviews_df.groupby('ReviewText')['Rating'].mean()
average_ratings_df = average_ratings_by_review.reset_index()
average_ratings_df.columns = ['CommonReviews', 'AverageRating'] # Rename columns for clarity
merged_df_left = pd.merge(common_reviews_df, average_ratings_df, on='CommonReviews', how='left')
print(merged_df_left.head())
# Add average rating column per common review
average_sentiment_by_review = customer_reviews_df.groupby('ReviewText')['SentimentScore'].mean()
average_sentiment_df = average_sentiment_by_review.reset_index()
average_sentiment_df.columns = ['CommonReviews', 'AverageSentimentScore'] # Rename columns for clarity
merged_df_left = pd.merge(merged_df_left, average_sentiment_df, on='CommonReviews', how='left')
# Apply sentiment categorization using both text and rating
merged_df_left['AverageSentimentCategory'] = merged_df_left.apply(
    lambda row: categorize_sentiment(row['AverageSentimentScore'], row['AverageRating']), axis=1)
# Apply sentiment bucketing to categorize scores into defined ranges
merged_df_left['AverageSentimentBucket'] = merged_df_left['AverageSentimentScore'].apply(sentiment_bucket)

print(merged_df_left.head())
# Output to csv
merged_df_left.to_csv('C:/Users/asia9/OneDrive/Desktop/ShopEasy_MarketingAnalysis_CaseStudy/Python/clean_common_reviews.csv', index=False)

# Display the first few rows of the DataFrame with sentiment scores, categories, and buckets
print(customer_reviews_df.head())
# Save the DataFrame with sentiment scores, categories, and buckets to a new CSV file
customer_reviews_df.to_csv('C:/Users/asia9/OneDrive/Desktop/ShopEasy_MarketingAnalysis_CaseStudy/Python/customer_reviews_with_sentiment.csv', index=False)
