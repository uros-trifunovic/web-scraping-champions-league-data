# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from functions import get_table_headers_links
from functions import get_all_club_stats


# The link to the champions league website containing team statistics
cl_data_link = 'https://www.uefa.com/uefachampionsleague/season=2021/statistics/round=2001252/clubs/index.html'

# Store the links to the pages containing team statistics
table_headers_links = get_table_headers_links(cl_data_link)

# Retrieve statistics for all the teams
clubs_dict = get_all_club_stats(table_headers_links)

# Store all teams statistics in a pandas DataFrame
df_teams_stats = pd.DataFrame(clubs_dict).transpose()
pd.set_option('display.max_columns', None)

print(df_teams_stats)

# Examine a few rows
df_teams_stats.head()

# Examine the data types
print(df_teams_stats.dtypes)

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
print(df_teams_stats.dtypes)

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
# Adj. R-squared of 0.839 indicate that teams who score goals
# with a right foot from the inside area are more likely to win

# To confirm the hypothesis, we narrow the focus down to the teams
# who won all their games to better understand their style
best_teams_stats = df_teams_stats[df_teams_stats['Wins'] > 3]
print(best_teams_stats)

# We look at the correlation matrix to see which variables impact the outcome of the best teams' games the most
df_corr_matrix = best_teams_stats.corr().dropna(how='all').dropna(axis='columns')
fig, ax = plt.subplots(figsize=(20, 10))
sns.heatmap(df_corr_matrix, annot=True, fmt='.1g')
plt.show()

# Here, the correlation matrix shows a different story. There
# is a negative correlation of -0.8 between the number of goals
# scored and the the number of goals scored with a right foot.
# Additionally, there is a strong positive correlation between
# the number of goals scored and the number of goals scored with
# either a left foot or a head. It is possible that the opposite
# teams focus on marking the right feet of these teams' players,
# leaving more room for either a header or a shoot with a left foot.
# The top three teams are good enough to take advantage of such opportunity.
