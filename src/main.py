'''
--- NOTA IMPORTANTE: ---
Para ejecutar el código correctamente, asegurate de agregar a la carpeta local el archivo cookies.json que se encuentra en el drive.
'''



from twikit import Client, TooManyRequests
import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
import asyncio
import json


MINIMUM_TWEETS = 30
USERNAME = 'metrodemedellin'
QUERY = '(llegar OR llego OR voy OR ruta) (@metrodemedellin) lang:es'

async def get_tweets(client, tweets):
    if tweets is None:
        print(f'{datetime.now()} - Getting tweets...')
        # Get tweets
        tweets = await client.search_tweet(QUERY, product='Top')

    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds...')
        await asyncio.sleep(wait_time)
        tweets = await tweets.next()
    return tweets
        

async def get_replies(client, conversation_id):
    """ Obtiene respuestas a un tweet específico usando conversation_id_str """
    # replies = await client.search_tweet(f"conversation_id:{conversation_id}", product="Latest")
    # return replies
    if not conversation_id:
        return []
    
    query = f"conversation_id:{conversation_id}"
    #& print(f"Searching replies with query: {query}")  # Agregar este print

    replies = await client.search_tweet(query, product="Latest")
    
    extracted_replies = []
    
    #& print(f"Replies found: {len(replies) if replies else 0}")
    
    if not replies:
        print(f"No replies found for conversation_id: {conversation_id}")
        
    else: 
        for reply in replies:
            #& print(json.dumps(reply._data, indent=2, ensure_ascii=False))
            if hasattr(reply, "_data") and "legacy" in reply._data and "full_text" in reply._data["legacy"]:
                extracted_replies.append(reply._data["legacy"]["full_text"])
    
    return extracted_replies


async def main():
    # Login credentials
    config = ConfigParser()
    config.read('config.ini')

    username = config['X']['username']
    email = config['X']['email']
    password = config['X']['password']
    
    
    # Create csv file
    with open('tweets.csv', 'w', newline='', encoding='utf-8-sig') as file:   # 'w': write mode
        writer = csv.writer(file)
        writer.writerow(['No.', 'Username', 'Text', 'Created at', 'Likes', 'Conversation ID', 'Reply count', 'Replies text', 'URL'])
       

    # Authenticate to the website (X.com)
    #! There are two methods: 1) use the login credentials. 2) use cookies.
    client = Client(language='es')
    #await client.login(auth_info_1=username, auth_info_2=email, password=password)
    #client.save_cookies('cookies.json')
    
    client.load_cookies('cookies.json')
    
    tweet_count = 0
    tweets = None
    
    while tweet_count < MINIMUM_TWEETS:
        try:
            tweets = await get_tweets(client, tweets)
        except TooManyRequests as e:
            rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
            print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
            wait_time = rate_limit_reset - datetime.now()
            await asyncio.sleep(max(wait_time.total_seconds(), 0))
            continue
            

        if not tweets:
            print(f'{datetime.now()} - No more tweets found...')
            break

        for tweet in tweets:
            tweet_count += 1

            # ------
            # Extract extended URL if exists
            expanded_urls = []
            if hasattr(tweet, "entities") and "urls" in tweet.entities:
                expanded_urls = [url["expanded_url"] for url in tweet.entities["urls"]]
            
            # Verify if the tweet has gata in '_data' and 'legacy'
            if hasattr(tweet, '_data') and 'legacy' in tweet._data:
                legacy_data = tweet._data['legacy']

                # Verify if 'extended_entities' is in 'legacy'
                if 'extended_entities' in legacy_data:
                    media_list = legacy_data['extended_entities']['media']

                    for media in media_list:
                        expanded_urls.append(media.get('expanded_url', 'No expanded URL'))
                else:
                    print(f'Tweet {tweet_count}: No extended entities')

            else:
                print(f'Tweet {tweet_count}: No legacy in _data')
            
            # ------
            if "legacy" in tweet._data and "conversation_id_str" in tweet._data["legacy"]:
                conversation_id = tweet._data["legacy"]["conversation_id_str"]
            else:
                conversation_id = None
                
            replies = await get_replies(client, conversation_id) if conversation_id else []

            tweet_data = [tweet_count,
                        tweet.user.name,
                        tweet.text,
                        tweet.created_at,
                        tweet.favorite_count,
                        conversation_id,
                        tweet.reply_count,
                        "; ".join(replies),
                        expanded_urls                        
            ]
            
            with open('tweets.csv', 'a', newline='', encoding='utf-8-sig') as file:   # 'a': append mode
                writer = csv.writer(file)
                writer.writerow(tweet_data)
                
            print(tweet_data)
            #& print(json.dumps(tweet._data, indent=2, ensure_ascii=False))
        

        print(f'{datetime.now()} - Done! Got {tweet_count} tweets')

asyncio.run(main())


print('Done!')  
