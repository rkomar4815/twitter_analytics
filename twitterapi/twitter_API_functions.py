import twitter
import local_settings
import pandas as pd
import tweepy
import json
import codecs
import shutil
import os


'''

Gets all the Twitter IDs of a selected user's followers or friends as a list.
Breaks the ID list into chunks of chunk_size.

If the total number of followers or friends isn't divisible by your chunk_size,
the last chunk will be smaller than your specified chunk_size.

'''


def GetIDs(user_id, api_type, api_requestsize, chunk_size):
    api = twitter.Api(
        consumer_key=local_settings.CONSUMER_KEY,
        consumer_secret=local_settings.CONSUMER_SECRET,
        access_token_key=local_settings.ACCESS_TOKEN,
        access_token_secret=local_settings.ACCESS_TOKEN_SECRET,
        sleep_on_rate_limit=True
    )

    if api_type == 'followers':
        follower_IDs = api.GetFollowerIDs(
            user_id=user_id, count=api_requestsize
        )

        follower_IDs = [follower_IDs[
            i * chunk_size:(i + 1) * chunk_size
        ] for i in range(
            (len(
                follower_IDs
            ) + chunk_size - 1) // chunk_size)]
        return(follower_IDs)

    elif api_type == 'friends':
        friend_IDs = api.GetFriendIDs(
            user_id=user_id, count=api_requestsize
        )
        friend_IDs = [friend_IDs[
            i * chunk_size:(i + 1) * chunk_size
        ] for i in range((len(friend_IDs) + chunk_size - 1) // chunk_size)]

        return(friend_IDs)

    else:
        print("Error! api_type must be 'friends' or 'followers'")


'''

Gets Twitter user objects for a list of  up to 100 user IDs as a JSON.
Converts JSON into a JSON formatted list of nested dictionaries.

'''


def getuserinfo(user_id):
    api = twitter.Api(
        consumer_key=local_settings.CONSUMER_KEY,
        consumer_secret=local_settings.CONSUMER_SECRET,
        access_token_key=local_settings.ACCESS_TOKEN,
        access_token_secret=local_settings.ACCESS_TOKEN_SECRET,
        sleep_on_rate_limit=True
    )

    jsonformattedlist = api.UsersLookup(
        user_id=user_id,
        screen_name=None,
        include_entities=False,
        return_json=True)

    return jsonformattedlist


'''

Converts a JSON formatted list of nested dictionaries into a Pandas dataframe.
Drops irrelevant columns and data from the dataframe.

'''


def userobject_dataframer(jsonformattedlist):
    twitter_df = pd.io.json.json_normalize(jsonformattedlist)
    columns_to_keeplist = [
        'created_at', 'description',
        'favourites_count', 'followers_count',
        'friends_count', 'id', 'location', 'name',
        'screen_name', 'statuses_count', 'verified'
    ]

    twitter_df = twitter_df.loc[:, columns_to_keeplist]

    return twitter_df


'''

Iterates over a chunked json-formatted list to get Twitter user objects.
Creates a dataframe with the resulting output of userobjects.

'''


def usergetiterator(user_id, api_type, api_requestsize, chunk_size):

    IDlist = GetIDs(user_id, api_type, api_requestsize, chunk_size)

    userobject_df = pd.DataFrame(index=None, columns=None)

    for IDchunk in IDlist:

        jsonformattedlist = getuserinfo(IDchunk)

        IDchunk_df = userobject_dataframer(jsonformattedlist)

        userobject_df = userobject_df.append(
            IDchunk_df, sort=True,
            ignore_index=True
        )

    return userobject_df


'''

Gets up to 3,200 of a user's latest tweet statuses.
Returns a JSON-formatted list of tweet data.

'''


def get_user_statuses(
        user_id, api_requestsize,
        exclude_replies=True, include_rts=False):

    consumer_key = local_settings.CONSUMER_KEY
    consumer_secret = local_settings.CONSUMER_SECRET
    access_key = local_settings.ACCESS_TOKEN
    access_secret = local_settings.ACCESS_TOKEN_SECRET

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    tweet_statuses = []

    latest_tweets = api.user_timeline(
        user_id=user_id, count=api_requestsize,
        tweet_mode='extended', exclude_replies=exclude_replies,
        include_rts=include_rts)

    tweet_statuses.extend(latest_tweets)

    oldest_status = tweet_statuses[-1].id - 1

    while len(latest_tweets) > 0:
        latest_tweets = api.user_timeline(
            user_id=user_id, count=200, max_id=oldest_status,
            tweet_mode='extended', exclude_replies=exclude_replies,
            include_rts=include_rts)

        # save the most recent tweets
        tweet_statuses.extend(latest_tweets)

        #  update the id of the oldest tweet minus one
        oldest_status = tweet_statuses[-1].id - 1

    return tweet_statuses  # list of JSON formatted tweets


'''

Writes JSON data from a JSON formatted list to a JSON file in a directory.
Dumptype gets concatenated to the end of your filename to differentiate
the JSON file from other JSON files with the same user_id.

'''


def JSONdumper(user_id, JSONformattedlist, dumptype):
    for x in JSONformattedlist:
        filename = str(user_id) + dumptype

        with codecs.open(filename, "a", "utf-8", "ignore") as jsonout:
            json.dump(
                x._json, jsonout,
                ensure_ascii=False, sort_keys=True,
                indent=4
            )
            jsonout.write('\n')

    return filename


'''

Moves files from one directory to another.

'''


def filemover(filename, destinationdirectory):
    filepath = os.getcwd() + '/' + filename

    filedestinationpath = os.getcwd() + destinationdirectory + filename

    shutil.move(src=filepath, dst=filedestinationpath)

    filepath = filedestinationpath

    return filepath


'''

Reads JSON file to JSON formatted list.

'''


def JSONread(filepath):

    JSONformattedlist = []

    with open(filepath, 'r') as f:
        for line in f:
            JSONformattedlist.append(json.loads(line))

    return JSONformattedlist


if __name__ == "__main__":
    
    statuses = get_user_statuses(15361570, 200)
    filename = JSONdumper(15361570, statuses, '_status.JSON')
    filepath = filemover(filename, '/usertweets/')

    test = JSONread(filepath)
    test_frame = pd.DataFrame(test)
    test_frame.to_csv('test.csv')
