#!pipenv run python3
import sys, getopt
from neo4j import GraphDatabase
import os
import json

MAX_BATCH_LENGTH = 5000

def load_tweets_in_batches(filename):
    batches = []
    tweets = []

    fp = open(filename, "r")

    line = 1
    while True:
        try:
            line = fp.readline()
            if not line: break
            
            tweets.append(json.loads(line))
            line = line + 1

            if len(tweets) > MAX_BATCH_LENGTH:
                batches.append(tweets)
                tweets = []
        except Exception as e:
            print("Error on line %d: %s" % (line, e))
            break

    fp.close()
    batches.append(tweets)
    return batches


LOAD_TWEETS_CYPHER = """
UNWIND $events AS event
MERGE (c:Conversation { id: event.conversation_id })
MERGE (u:User { username: event.username })
   ON CREATE SET u.id = toString(event.user_id), u.name = event.name
   ON MATCH SET u.name = event.name
MERGE (t:Tweet {
    id: event.id
})
    ON CREATE SET
        t.created = datetime(event.date + "T" + event.time + coalesce(event.timezone, "Z")),
        t.tweet = event.tweet,
        t.link = event.link,
        t.retweet = event.retweet,
        t.geo = event.geo,
        t.source = event.source,
        t.likes = event.likes_count,
        t.retweets = event.retweets_count,
        t.replies = event.replies_count
MERGE (u)-[:TWEET]->(t)
MERGE (t)-[:IN]->(c)

WITH t, event
UNWIND event.hashtags as hashtag
MERGE (h:Hashtag { name: hashtag })
MERGE (t)-[:TAG]->(h)

WITH t, event
UNWIND event.mentions AS mention
MERGE (mentionedUser:User { username: mention })
MERGE (t)-[:MENTIONS]->(mentionedUser)

WITH t, event
UNWIND event.reply_to as reply_to
MERGE (repUser:User { username: reply_to.username })
    ON CREATE SET repUser.id = toString(reply_to.user_id)
MERGE (t)-[:REPLY_TO]->(repUser)

WITH t, event
UNWIND event.urls as url
MERGE (u:URL { url: url })
MERGE (t)-[:URL]->(u)

WITH t, event
UNWIND event.photos as photo
MERGE (p:URL { url: photo })
   ON CREATE SET p.photo = true
MERGE (t)-[:PHOTO]->(p)
RETURN count(t);
"""

def load_tweets(driver, batch):
    def tweet_batch(tx):
        tx.run(LOAD_TWEETS_CYPHER, events=batch)
    
    with driver.session() as session:
        res = session.write_transaction(tweet_batch)
        print(res)
        return res

def main(argv):
    inputfile = ''
    
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print ('import-tweets.py -i tweets.json')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('import-tweets.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg

    if not inputfile:
        print ('import-tweets.py -i <inputfile>')
        sys.exit(1)

    print("Creating neo4j driver")
    uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "admin")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    print("Loading tweets from %s" % inputfile)
    batches = load_tweets_in_batches(inputfile)

    for batch in batches:
        load_tweets(driver, batch)
    driver.close()
    print("Done!")

if __name__ == "__main__":
   main(sys.argv[1:])

