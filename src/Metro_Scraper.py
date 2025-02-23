'''
Scraper de Twitter para buscar comentarios relacionados con "cómo llegar" al Metro de Medellín.
'''

import tweepy
import csv
import time

# Configura las credenciales de la API de Twitter
BEARER_TOKEN = '|1AAAAAAAAAAAAAAAAAAAAAGcIzgEAAAAA5bnPKpjWrCBS2ExDs7Lm%2BTBhWkc%3DbokIku7lvunDE2g1JEH8inAtSMqFqCudFwAvu5IU8rHwkTYVPR'  # Reemplaza con tu Bearer Token

# Inicializa el cliente de Tweepy
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Palabras clave para buscar comentarios relacionados con "cómo llegar"
query = "cómo llegar desde (metro de medellín OR medellín) -filter:retweets"

# Archivo CSV para guardar los resultados
output_file = 'comentarios_metro_medellin.csv'

# Función para buscar tweets y clasificarlos
def buscar_comentarios(query, max_results=100):
    try:
        # Realiza la búsqueda de tweets
        tweets = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["created_at", "public_metrics", "author_id"],
            user_fields=["username"],
            expansions=["author_id"]
        )

        # Procesa los tweets encontrados
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Fecha", "Usuario", "Texto", "Likes", "Retweets"])

            for tweet in tweets.data:
                # Obtiene el nombre de usuario
                user = next(user for user in tweets.includes['users'] if user.id == tweet.author_id)
                username = user.username

                # Escribe los datos en el archivo CSV
                writer.writerow([
                    tweet.created_at,
                    username,
                    tweet.text,
                    tweet.public_metrics['like_count'],
                    tweet.public_metrics['retweet_count']
                ])

                print(f"Tweet de @{username}: {tweet.text}\n")

    except tweepy.TweepyException as e:
        print(f"Error al buscar tweets: {e}")

# Ejecuta la búsqueda
print("Buscando comentarios sobre 'cómo llegar' en el Metro de Medellín...")
buscar_comentarios(query, max_results=50)  # Limita a 50 tweets para evitar sobrecargar la API
print(f"Los resultados se han guardado en {output_file}")