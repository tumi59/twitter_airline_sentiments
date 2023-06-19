import requests
import re
import csv
from pprint import pprint
from airlines import get_airline_names
from sentiment2 import get_sentiment

def parse_page(subreddit, after='', writer=None):

    # Get the list of airline names
    airline_names = get_airline_names()

    url_template = 'https://www.reddit.com/r/{}/top.json?t=all{}' 

    headers = {
    'User-Agent' : 'VirboxBot'
    }

    params = f'&after={after}' if after else ''

    post_count = 0

    while True:
        url = url_template.format(subreddit, params)
        response = requests.get(url, headers=headers)

        if response.ok:
            data = response.json()['data']
            for post in data['children']:
                pdata = post['data']
                post_id= pdata['id']
                title = pdata['title']
                body = pdata['selftext']
                score = pdata['score']
                author = pdata['author']
                date = pdata['created_utc']
                url = pdata.get('url_overridden_by_dest')

                sentiment = get_sentiment(body)
                print(sentiment)

                # Only write the post to the CSV file if its title or body contains the name of an airline
                for airline_name in airline_names:
                    # Use regex to ensure the full name is present
                    if (re.search(r'\b' + re.escape(airline_name.lower()) + r'\b', title.lower()) or
                        re.search(r'\b' + re.escape(airline_name.lower()) + r'\b', body.lower())):  # Check body as well
                        try:
                            writer.writerow([post_id, score, title, body, sentiment])  # Write the data into the CSV file
                            post_count += 1
                            if post_count >= 100:
                                return None  # Stop scraping after writing 100 posts
                        except Exception as e:
                            print(f"Error writing post {post_id} to CSV: {e}")
                        break
            
            if 'after' in data and data['after'] is not None:
                params = '&after=' + data['after']
            else:
                print(f"'after' not found in 'data'. 'data' is: {data}")
                return '****Can\'t retrive post****'
        else:
            print(f'Error {response.status_code}')
            return '****Can\'t retrive post****'

def main():
    subreddit = 'Flights'
    after = ''
    with open('output.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Post ID", "Score", "Title", "Body", "Sentiment Analysis Result"])  # Added "Sentiment Analysis Result" to CSV header
        while True:
            after = parse_page(subreddit, after, writer)
            if after is None:
                break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Stoping scrape........')
