import requests
import re
import csv
from pprint import pprint
import sqlite3
from airlines import get_airline_names
from sentiment2 import get_sentiment

def create_table(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            title TEXT,
            body TEXT,
            score INTEGER,
            author TEXT,
            data REAL,
            url TEXT,
            sentiment TEXT
        )
    ''')
    conn.commit()

def parse_page(subreddit, after='', conn=None, post_limit=1000):

    # Get the list of airline names
    airline_names = get_airline_names()

    url_template = 'https://www.reddit.com/r/{}/top.json?t=all{}' 

    headers = {
    'User-Agent' : 'VirboxBot'
    }

    params = f'&after={after}' if after else ''

    global_post_count = 0  # Global post counter

    while global_post_count < post_limit:
        url = url_template.format(subreddit, params)
        response = requests.get(url, headers=headers)

        if response.ok:
            c = conn.cursor()
            data = response.json()['data']
            for post in data['children']:
                if global_post_count >= post_limit:
                    return None  # Return None to stop the loop in main()
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
                c.execute('INSERT OR IGNORE INTO posts VALUES (?,?,?,?,?,?,?,?)',
                          (post_id, title, body, score, author, date, url, sentiment))
                global_post_count += 1  # Increment the global post counter
            conn.commit()
            if 'after' in data and data['after'] is not None:
                params = '&after=' + data['after']
            else:
                print(f"'after' not found in 'data'. 'data' is: {data}")
                return None
        else:
            print(f'Error {response.status_code}')
            return None
        
    return None  # Return None when post limit is reached

        
def drop_table(conn):
    c = conn.cursor()
    c.execute('''
        DROP TABLE IF EXISTS posts
    ''')
    conn.commit()

if __name__ == '__main__':
    subreddit = 'Flights'

    conn = sqlite3.connect('reddit-posts.db')
    drop_table(conn)
    create_table(conn)

    after = ''
    try:
        while True:
            after = parse_page(subreddit, after, conn)
            if after is None:
                break
    except KeyboardInterrupt:
        print ('Stoping scrape...'  )
    finally:
        conn.close()
  
