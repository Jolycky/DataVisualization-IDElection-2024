import streamlit as st
import pandas as pd
import plotly.express as px
from nltk.tokenize import sent_tokenize
import numpy as np

conn = st.connection("mydb", type="sql", autocommit=True)

df = conn.query('SELECT EnglishPromotionName, StartDate, EndDate, MaxQty from dimpromotion limit 10;', ttl=600)


chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

st.bar_chart(chart_data)
st.table(df)

 
# Set the page icon
st.set_page_config(page_title="Indonesia Election 2024", 
                   page_icon=":bar_chart:",
                   initial_sidebar_state="expanded")

# Load the dataframe
@st.cache_data
def load_data(file):
    data = pd.read_csv(file, encoding='utf8')
    
    # Convert the 'Date' column to datetime format
    data['Date'] = pd.to_datetime(data['Date'])
    
    return data
# Load the data

df = load_data("indonesia-election-2024-dataset.csv")

# Adjust column widths
column_widths = {
    'Date': 50,
    'Title': 200,
    'Text': 300,
    'Publication': 50
}

# Calculate total width
total_width = sum(column_widths.values())

# Set the page title
st.title("Indonesia Election 2024")

# Sidebar menu
option = st.sidebar.selectbox("Select a feature", ["Data Visualisation", "Search News"])

if option == "Data Visualisation":
    import plotly.express as px

    # Define a custom color scale for each publication
    color_scale = px.colors.qualitative.Set2

    # Owner Name
    st.header("Owner Name")
    st.markdown("This application is created by [Jose Bagus Ramadhan](https://www.linkedin.com/in/josebagus/) \n(21082010206).")
    
    # Data Visualisation page
    st.header("Data Visualisation")

    st.text("The data ranges from 2023-11-29 to 2024-02-06 and includes all five\npresidential debates organized by the General Elections Commission.\nThe data sources comprise detik, kompas, and liputan6.")
    
    # Article Count per Publication
    st.subheader("Article Count per Publication")

    st.text("The length of each bar represents the number of articles, and\neach bar is color-coded to represent a different publication.")

    chart_data_total = df.groupby('Publication').size().reset_index(name='Total Article')
    fig = px.bar(chart_data_total, x='Total Article', y='Publication', orientation='h', color='Publication', color_discrete_sequence=color_scale)
    fig.update_layout(width=700, height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Function to count word frequency in titles
    def count_word_frequency_in_titles(data: pd.DataFrame, words: list) -> pd.DataFrame:
        word_frequency = {word: 0 for word in words}

        for title in data['Title']:
            for word in words:
                # Check for the word Muhaimin and Imin
                if word.lower() in title.lower() or (word.lower() == 'muhaimin' and 'imin' in title.lower()):
                    word_frequency[word] += 1

        return pd.DataFrame(list(word_frequency.items()), columns=['Word', 'Frequency'])

    # Words to count frequency for
    words_to_count = ['Anies', 'Muhaimin', 'Amin', 'Prabowo', 'Gibran', 'Ganjar', 'Mahfud']

    # Display the bar chart
    st.subheader("Candidate Mentions in Titles")

    st.text("Anies-Muhaimin is the only candidate pair with an official tagline called 'Amin'.\nAs a result, there are articles where the tagline is used interchangeably with\ntheir names, requiring separate treatment in visualising the data. Additionally,\nMuhaimin is sometimes referred to as 'Imin', 'Gus Imin' or 'Cak Imin', which\nmust be accounted for in the visualisation.")

    word_freq_df = count_word_frequency_in_titles(df, words_to_count)

    # Update the label for 'Muhaimin' to 'Muhamain' in the DataFrame
    word_freq_df.loc[word_freq_df['Word'] == 'Muhaimin', 'Word'] = 'Muhaimin'

    fig = px.bar(word_freq_df, x='Frequency', y='Word', orientation='h', color='Word', 
                color_discrete_sequence=color_scale)
    fig.update_layout(width=700, height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Function to count word frequency in titles for each publication
    def count_word_frequency_in_titles_per_publication(data: pd.DataFrame, words: list) -> pd.DataFrame:
        word_frequency_per_pub = {pub: {word: 0 for word in words} for pub in data['Publication'].unique()}

        for pub in data['Publication'].unique():
            pub_data = data[data['Publication'] == pub]
            for title in pub_data['Title']:
                for word in words:
                    if word.lower() in title.lower() or (word.lower() == 'muhaimin' and 'imin' in title.lower()):
                        word_frequency_per_pub[pub][word] += 1

        return pd.DataFrame(word_frequency_per_pub).transpose()

    # Words to count frequency for
    words_to_count = ['Anies', 'Muhaimin', 'Amin', 'Prabowo', 'Gibran', 'Ganjar', 'Mahfud']

elif option == "Search News":

    # Search function
    st.header("Search News")
    st.text("Enter a keyword or a phrase to search for relevant news articles.")

    search_query = st.text_input("Keyword to search for")

    if search_query:
        # Filter the dataframe based on the search query
        filtered_df = df[df['Text'].str.contains(search_query, case=False)]

        # Display the search results
        st.write(f"### Search Results for \"{search_query}\"")
        st.dataframe(filtered_df[['Date', 'Title', 'Text', 'Publication']], width=total_width, height=None, use_container_width=True)
