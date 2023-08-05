import requests
import sqlite3
import re
from airlines import get_airline_names
from sentiment2 import get_sentiment

# create sqp table with all columns names and data types
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
            sentiment TEXT,
            airline TEXT
        )
    ''')
    conn.commit()

# row counting method used so that the scraping scirpt knows when to stop
def count_rows(conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM posts")
    rows = c.fetchone()[0]
    return rows

# parses throught the subreddit's json file
def parse_page(subreddit, after='', conn=None, post_limit=1000):

    # get the list of airline names from api
    airline_names = get_airline_names()

    # link to the subreddit
    url_template = 'https://www.reddit.com/r/{}/top.json?t=all{}' 

    # intialize scraping bot
    headers = {
    'User-Agent' : 'VirboxBot'
    }

    params = f'&after={after}' if after else ''

    # endless loop to continue scraping
    while True:
        url = url_template.format(subreddit, params)
        response = requests.get(url, headers=headers)

        # store specific info from each scrapped post
        if response.ok:
            c = conn.cursor()
            data = response.json()['data']
            for post in data['children']:
                pdata = post['data']
                post_id = pdata['id']
                title = pdata['title']
                body = pdata['selftext']
                score = pdata['score']
                author = pdata['author']
                date = pdata['created_utc']
                url = pdata.get('url_overridden_by_dest')

                # skip if body of post is less than 100 words
                if len(body.split()) < 100:
                    continue
                
                # check if post or title explicity mentions an airline name
                for airline in airline_names:
                    pattern = f'\\b{airline.lower()}\\b'
                    if re.search(pattern, title.lower()) or re.search(pattern, body.lower()):
                        sentiment = get_sentiment(body)
                        print(sentiment)
                        c.execute('INSERT OR IGNORE INTO posts VALUES (?,?,?,?,?,?,?,?,?)',
                                (post_id, title, body, score, author, date, url, sentiment, airline))
                        conn.commit()

                        if count_rows(conn) >= post_limit:
                            return None 
        
                        break
        else:
            # if theres an error reading post, print error but skip to next post
            print(f'Error {response.status_code}')
            # don't return None. Instead, continue
            continue

        if 'after' in data and data['after'] is not None:
            params = '&after=' + data['after']
        else:
            print(f"'after' not found in 'data'. 'data' is: {data}")
            # keep scraping from start if after variable is not found
            params = ''

# delete existing table if one already exists when running the program         
def drop_table(conn):
    c = conn.cursor()
    c.execute('''
        DROP TABLE IF EXISTS posts
    ''')
    conn.commit()

# call functions and start scraping 
if __name__ == '__main__':
    subreddit = 'Flights'

    conn = sqlite3.connect('reddit-posts.db')
    drop_table(conn)
    create_table(conn)

    after = ''
    try:
        while True:
            after = parse_page(subreddit, after, conn, post_limit=1000)
            if after is None:
                break
    except KeyboardInterrupt:
        print ('Stoping scrape...'  )
    finally:
        conn.close()
