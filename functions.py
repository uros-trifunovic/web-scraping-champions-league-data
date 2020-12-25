import requests
from bs4 import BeautifulSoup

# Takes the link to the webpage as an argument and returns
# the list of links to the pages containing team statistics

clubs_dict = {}


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
        # Check if the loop is at the "Overview" header and appropriately append the link to the list in either case
        if header_name == 'overview':
            table_headers_links.append('')
        else:
            table_headers_links.append('/kind=' + header_name)

    # Return the list containing all the links
    return table_headers_links


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
                    # - the value dictionary has the column name as key and column statistics as value
                    #   (e.g. "'Wins' : '3'")
                    clubs_dict[club] = {
                        header_name: club_data_categories[i].get_text()}

                    # Increment the count variable
                    i += 1
                else:

                    # If the club has already been added to the dictionary, update the dictionary in the same way as
                    # above
                    clubs_dict[club].update(
                        {header_name: club_data_categories[i].get_text()})
                    i += 1

    # Return the dictionary containing all the clubs names and statistics
    return clubs_dict


# Takes the list of links containing team statistics as an input
# For each link it the list, it calls a function to read in team statistics


def get_all_club_stats(links):

    result_dict = {}

    # Loop through the links in the provided list
    for header_link in links:
        # Store the link appropriately
        link = 'https://www.uefa.com/uefachampionsleague/season=2021/statistics/round=2001252/clubs' + \
               header_link + '/index.html'

        # Call the function to extract team statistics from the link passed as an argument
        result_dict = get_categorical_club_stats(link)

    return result_dict
