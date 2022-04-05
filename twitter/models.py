from django.db import models

from twitter.core.dataset import Tweet as TweetObj, TwitterUser as TwitterUserObj


class Tweet(models.Model):
    text = models.TextField(null=True)
    tweet_id = models.BigIntegerField(null=True)
    user = models.ForeignKey('TwitterUser', related_name='tweets', on_delete=models.DO_NOTHING, null=True)
    retweet_count = models.IntegerField(default=0)
    tweet_created_date = models.DateTimeField(null=True, blank=True)
    like_count = models.IntegerField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def parse_tweet_obj(self, tweet: TweetObj):
        self.text = tweet._text
        self.like_count = tweet.like_count
        self.tweet_id = tweet.tweet_id
        self.retweet_count = tweet.retweet_count
        self.tweet_created_date = tweet.tweet_created_date
        try:
            if tweet.user.db_id is not None:
                user = TwitterUser.objects.get(twitter_id=tweet.user.db_id)
            else:
                user = TwitterUser()
                user.parse_twitter_user(twitter_user=tweet.user)
        except TwitterUser.DoesNotExist:
            user = TwitterUser()
            user.parse_twitter_user(twitter_user=tweet.user)
        self.user = user
        self.save()
        tweet.db_id = self.id


class TwitterUser(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    twitter_id = models.BigIntegerField(null=True)
    twitter_handle = models.CharField(max_length=100, null=True)
    followers_count = models.IntegerField(null=True)
    friends_count = models.IntegerField(null=True)
    listed_count = models.IntegerField(null=True)
    statuses_count = models.BigIntegerField(null=True)
    friends = models.ManyToManyField('TwitterUser', related_name='twitter_friends')
    followers = models.ManyToManyField('TwitterUser', related_name='twitter_followers')
    twitter_user_created_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def parse_twitter_user(self, twitter_user: TwitterUserObj):
        self.name = twitter_user.name
        self.twitter_id = twitter_user.twitter_id
        self.twitter_handle = twitter_user.twitter_handle
        self.followers_count = twitter_user.followers_count
        self.friends_count = twitter_user.friends_count
        self.listed_count = twitter_user.listed_count
        self.twitter_user_created_at = twitter_user.created_at
        self.description = twitter_user.description
        self.statuses_count = twitter_user.statuses_count
        self.save()
        twitter_user.db_id = self.id


class CrawlerTasks(models.Model):
    starting_token = models.CharField(max_length=200, null=True)
    starting_user = models.BigIntegerField(help_text='the Twitter id of the user', null=True)
    completed = models.BooleanField(default=False)
    crawl_friends = models.BooleanField(default=False)
    parent = models.ForeignKey('twitter.CrawlerTasks', on_delete=models.CASCADE, related_name='children', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
