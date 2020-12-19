# Import required libraries
import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

# Takes the link to the wepbage as an argument and returns
# the list of links to the pages containing team statistics


def get_table_headers_links(link):

    # Store the link information
    page = requests.get(link)

    # Parse the link information
    soup = BeautifulSoup(page.content, 'html.parser')

    # Locate the class containing the header information
    table_headers = soup.find(class_='nav-tabs')

    # Initiate an empty list to store the header links in
    table_headers_links = []

    # Loop through all the elements in the class
    for header in table_headers:

        # Store the header name
        header_name = header.get('id')

        # The link containing the overview of team statistics differs from the other headers links
        # Check if the loop is at the "Overview" header and apropriatelly append the link to the list in either case
        if header_name == 'overview':
            table_headers_links.append('')
        else:
            table_headers_links.append('/kind=' + header_name)

    # Return the list containing all the links
    return(table_headers_links)

# Takes the link to team statistics as an argument and
# returns a dictionary containing team names and statistics


def get_categorical_club_stats(link):

    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Locate the element containing the header information
    club_stats_headers = soup.find('thead').find('tr')

    # Locate the table containing team statistics
    club_stats_data = soup.find('tbody').find_all('tr')

    # Loop through the table containing team statistics
    for club_data in club_stats_data:

        # Extract and store the club name
        club = club_data.find('a').get_text()

        # Locate all the team-specific statistics
        club_data_categories = club_data.find_all('td')

        # Initialize the count variable to be used for reading
        # data from multiple tables into the result dictionary
        i = 1

        # Loop through all the columns in the table
        for stat_header in club_stats_headers:

            # Extract and store the header name
            header_name = stat_header.get_text()

            # All the tables across different pages have team names as in the first column
            # We store the team name only once and, therefore, we skip such columns
            if header_name != 'Team':

                # Check if the club exists in the result dictionary
                if club not in clubs_dict:

                    # If not, add the entry to the result dictionary as follow:
                    # - key is the club name (e.g. "Bayern")
                    # - value for the key is another dictionary
                    # - the value dictionary has the column name as key and column statistics as value (e.g. "'Wins' : '3'")
                    clubs_dict[club] = {
                        header_name: club_data_categories[i].get_text()}

                    # Increment the count variable
                    i += 1
                else:

                    # If the club has already been added to the dictionary, update the dictionary in the same way as above
                    clubs_dict[club].update(
                        {header_name: club_data_categories[i].get_text()})
                    i += 1

    # Return the dictionary containing all the clubs names and statistics
    return(clubs_dict)

# Takes the list of links containing team statistics as an input
# For each link it the list, it calls a function to read in team statistics


def get_all_club_stats(links):

    # Loop through the links in the provided list
    for header_link in links:

        # Store the link appropriately
        link = 'https://www.uefa.com/uefachampionsleague/season=2021/statistics/round=2001252/clubs' + \
            header_link + '/index.html'

        # Call the function to extract team statistics from the link passed as an argument
        get_categorical_club_stats(link)


# Initiate an empty dictionary to store team statistics in
clubs_dict = {}

# The link to the champions league website containing team statistics
cl_data_link = 'https://www.uefa.com/uefachampionsleague/season=2021/statistics/round=2001252/clubs/index.html'

# Store the links to the pages containing team statistics
table_headers_links = get_table_headers_links(cl_data_link)

# Retrieve statistics for all the teams
get_all_club_stats(table_headers_links)

# Store all teams statistics in a pandas DataFrame
df_teams_stats = pd.DataFrame(clubs_dict).transpose()
pd.set_option('display.max_columns', None)

df_teams_stats

# Examine a few rows
df_teams_stats.head()

# Examine the data types
df_teams_stats.dtypes

# All the values in the DataFrame are of string type even though they are all numeric values
# Additionally, columns 'PC %', 'Average ball possession (%)', and 'Average ball possession (time)'
# have formatting as part of their values
# We can remove the formatting from values in the listed columns as the formatting is specified in the column names
df_teams_stats['PC %'] = df_teams_stats['PC %'].str.replace('%', '')
df_teams_stats['Average ball possession (%)'] = df_teams_stats['Average ball possession (%)'].str.replace(
    '%', '')
df_teams_stats['Average ball possession (time)'] = df_teams_stats['Average ball possession (time)'].str.replace(
    ' m', '')

# Confirm we have successfully removed the formatting from the values
df_teams_stats[[
    'Average ball possession (%)', 'Average ball possession (time)', 'PC %']].head()

# Now we can convert all the columns types to numeric
df_teams_stats = df_teams_stats.astype('float64')

# Confirm all the columns have type 'float64'
df_teams_stats.dtypes

# There are teams who won all their games as well as teams who lost all
df_teams_stats.describe()

# We look at the correlation matrix to see which variables impact the outcome of the games the most
df_corr_matrix = df_teams_stats.corr().dropna(how='all').dropna(axis='columns')
fig, ax = plt.subplots(figsize=(20, 10))
sns.heatmap(df_corr_matrix, annot=True, fmt='.1g')

# It appears that teams who win more often score more goals, on average.
# Furthermore, teams who get into the inside area more often tend to score more goals, on average.
# Interestingly, most of the goals scored from the inside area were scored with a right foot.
fig, axs = plt.subplots(ncols=3, figsize=(15, 5))
sns.regplot(x='Average scored', y='Wins', data=df_teams_stats, ax=axs[0])
sns.regplot(x='Inside area', y='Average scored',
            data=df_teams_stats, ax=axs[1])
sns.regplot(x='Inside area', y='Right foot', data=df_teams_stats, ax=axs[2])

# Considering the linear relationship between 'Wins' variable and 'Average scored', 'Inside area', and 'Right foot'
# variables, we can fit a linear regression model
result = sm.OLS(df_teams_stats['Wins'], df_teams_stats[[
                'Average scored', 'Inside area', 'Right foot']]).fit()
result.summary()
# Adj. R-squared of 0.839 indicate that teams who score goals with a right foot from the inside area are more likely to win

# To confirm the hypothesis, we narrow the focus down to the teams who won all their games to better understand their style
best_teams_stats = df_teams_stats[df_teams_stats['Wins'] > 3]
best_teams_stats

# We look at the correlation matrix to see which variables impact the outcome of the best teams' games the most
df_corr_matrix = best_teams_stats.corr().dropna(how='all').dropna(axis='columns')
fig, ax = plt.subplots(figsize=(20, 10))
sns.heatmap(df_corr_matrix, annot=True, fmt='.1g')
# Here, the correlation matrix shows a different story. There is a negative correlation of -0.8 between the number of goals
# scored and the the number of goals scored with a right foot. Additionally, there is a strong positive correlaton between
# the number of goals scored and the number of goals scored with either a left foot or a head. It is possible that the
# opposite teams focus on marking the right feet of these teams' players, leaving more room for either a header or a shoot
# with a left foot. The top three teams are good enough to take advantage of such opportunity.
