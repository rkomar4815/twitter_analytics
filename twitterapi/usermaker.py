import twitter_API_functions


class user_data(int):

    def __init__(self, user_id):
        self.user_id = user_id

    def followersinfo(self):
        followers_df = twitter_API_functions.usergetiterator(
            self.user_id, 'followers',
            5000, 100
        )
        return followers_df

    def friendsinfo(self):
        friends_df = twitter_API_functions.usergetiterator(
            self.user_id, 'friends',
            5000, 100
        )
        return friends_df


if __name__ == "__main__":

    x = user_data(15361570)
    print(x)
    testfollowersinfo = x.followersinfo()
    print(testfollowersinfo)
    testfriendsinfo = x.friendsinfo()
    print(testfriendsinfo)
