from abc import ABC
from typing import  Any

import tweepy
from tqdm import tqdm
from tweepy import AppAuthHandler, TweepError
from tweepy.models import User as TweepyUser, Status

from Argminer.celery import crawler_task
from core.crawler import Crawler
from core.dataset import DataPoint
from core.exceptions import NotSupportedException
from twitter.core.dataset import Tweet, TwitterUser, TwitterDataset,Dataset
from twitter.models import Tweet as TweetDB, TwitterUser as TwitterUserDB

import logging

logger = logging.getLogger(__name__)


class TwitterCrawler(Crawler, ABC):
    def __init__(self, consumer_key=None, consumer_secret=None) -> None:
        """
        This class if used to crawl twitter and extract users and tweets. This does not implement a crawling logic. This will
        take care of credentials management.
        :param consumer_key: Consumer Key obtained from twitter.
        :param consumer_secret: Consumer Secret obtained from twitter
        """
        self.consumer_key = "5pFpPxoMDcJpd6OaHyjfoWA1A" if consumer_key is None else consumer_key
        self.consumer_secret = "akg4oPOUDkx0RDVwAtuwyNd8TbF7C9MHct5pD0gabQVFhllv0E" if consumer_secret is None else \
            consumer_secret
        self.auth = AppAuthHandler(consumer_key=self.consumer_key, consumer_secret=self.consumer_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

    def fetch_tweets(self, keyword, tweet_count=100) -> tweepy.Cursor:
        return tweepy.Cursor(self.api.search, q=keyword, lang='en', count=tweet_count, extended=True,
                             tweet_mode='extended')

    def fetch_user(self, screen_name=None, user_id=None):
        return self.api.get_user(user_id if screen_name is None else screen_name)

    @staticmethod
    def fetch_friends(main_user: TwitterUser) -> TwitterDataset:
        user_dataset = TwitterDataset()
        for user in tweepy.Cursor(main_user.twitter_user_object.friends).items():
            user = TwitterUser(user=user)
            main_user.friends.append(user)
            user_dataset.append(user)
        return user_dataset

    @staticmethod
    def fetch_followers(main_user: TwitterUser) -> TwitterDataset:
        user_dataset = TwitterDataset()
        for user in tweepy.Cursor(main_user.twitter_user_object.followers).items():
            user = TwitterUser(user=user)
            main_user.followers.append(user)
        return user_dataset

    def get_full_text(self,tweet):
        status = self.api.get_status(tweet.id, tweet_mode="extended")
        try:
            full_text = status.retweeted_status.full_text
        except AttributeError:  # Not a Retweet
            full_text = status.full_text
        return full_text

class ArgumentCrawler(TwitterCrawler):
    def crawl(self,hashtag) -> None:
        super().crawl()
        tweets = self.fetch_tweets(hashtag)
        tweet_dataset = TwitterDataset()
        progress = tqdm()
        while True:
            try:
                search_tweets = tweets.iterator.next()
            except TweepError:
                continue
            except StopIteration:
                break
            for item in search_tweets:
                item.full_text = self.get_full_text(item)
                data = self._create_object(item,hashtag)
                tweet_dataset.append(data)
                # crawler_task.delay(parent_id=self.crawl_obj_id, starting_user=self.starting_user,
                #                     crawl_friends=self.crawl_friends)
                if self._is_useful_entity(data):
                    pass
                    # Todo: Need to decide on how to process a tweet. This is connected to is_useful_entity function.
                self._process_entity(tweet_dataset)
                progress.update()
        progress.close()
    
    def _create_object(self, crawl_data: Any,hashtag:str) -> DataPoint:
        if type(crawl_data) == TweepyUser:
            user = TwitterUser()
            user.parse_twitter_user(crawl_data)
            return user
        elif type(crawl_data) == Status:
            tweet = Tweet()
            tweet.parse_tweet_obj(hashtag, crawl_data)
            return tweet
        else:
            raise NotSupportedException(f"The type {type(crawl_data)} is not supported.")
    
    def _process_entity(self, dataset: TwitterDataset):
        if dataset.type == TwitterUser:
            for user in dataset:
                db_user = TwitterUserDB()
                db_user.parse_twitter_user(user)
        elif dataset.type == Tweet:
            for tweet in dataset:
                tweet : Tweet
                db_tweet = TweetDB()
                if not TweetDB.objects.filter(id=tweet.tweet_id).exists():
                    db_tweet.parse_tweet_obj(tweet)
        else:
            raise NotSupportedException(f"Dataset type is not supported for processing. Received Type: {dataset.type}")
    
    def _is_useful_entity(self, dataset: Dataset) -> bool:
        super()._is_useful_entity(dataset)
        return True

class CelebrityCrawler(TwitterCrawler):
    def __init__(self,
                 starting_token: str = None,
                 starting_user: TwitterUser = None,
                 follower_threshold=1e5,
                 like_threshold=1e3,
                 time_threshold_seconds=60 * 60 * 24,
                 crawl_obj_id=None,
                 crawl_friends=False,
                 consumer_key=None,
                 consumer_secret=None):
        super(CelebrityCrawler, self).__init__(consumer_key=consumer_key, consumer_secret=consumer_secret)
        self.starting_token = starting_token
        self.follower_threshold = follower_threshold
        self.time_threshold = time_threshold_seconds
        self.like_threshold = like_threshold
        self.starting_user = starting_user
        self.crawl_friends = crawl_friends
        self.crawl_obj_id = crawl_obj_id

    def crawl(self) -> None:
        if self.starting_user is not None:
            user = self.fetch_user(self.starting_user.twitter_id)
            user = TwitterUser(user)
            logger.info("Iterating over the user's {} friends".format(user))
            friends_dataset = self.fetch_friends(user)
            self._process_entity(friends_dataset)
            if self.crawl_friends:
                for friend in friends_dataset:
                    crawler_task.delay(parent_id=self.crawl_obj_id, starting_user=friend, crawl_friends=self.crawl_friends)
            # Dont fetch followers. It doesn't make sense for celebrities.
            # followers_dataset = self.fetch_followers(user)
            # self._process_entity(followers_dataset)
        else:
            tweets = self.fetch_tweets(self.starting_token)
            tweet_dataset = TwitterDataset()
            while True:
                try:
                    search_tweets = tweets.iterator.next()
                except TweepError:
                    continue
                except StopIteration:
                    break
                for item in search_tweets:
                    data = self._create_object(item)
                    tweet_dataset.append(data)
                    crawler_task.delay(parent_id=self.crawl_obj_id, starting_user=self.starting_user,
                                       crawl_friends=self.crawl_friends)
                    if self._is_useful_entity(data):
                        pass
                        # Todo: Need to decide on how to process a tweet. This is connected to is_useful_entity function.
                    self._process_entity(tweet_dataset)

    def _create_object(self, crawl_data: Any) -> DataPoint:
        if type(crawl_data) == TweepyUser:
            user = TwitterUser()
            user.parse_twitter_user(crawl_data)
            return user
        elif type(crawl_data) == Status:
            tweet = Tweet()
            tweet.parse_tweet_obj(self.starting_token, crawl_data)
            return tweet
        else:
            raise NotSupportedException(f"The type {type(crawl_data)} is not supported.")

    def _is_useful_entity(self, data: DataPoint) -> bool:
        if isinstance(data, TwitterUser) and data.followers_count >= self.follower_threshold:
            return True
        # As of now we are expanding only along user. Not through tweets.
        # if isinstance(data, Tweet) and datetime.now() - data.tweet_created_date > timedelta(
        #         seconds=self.time_threshold) and data.like_count > self.like_threshold:
        #     return True
        return False

    def _process_entity(self, dataset: TwitterDataset):
        if dataset.type == TwitterUser:
            for user in dataset:
                db_user = TwitterUserDB()
                db_user.parse_twitter_user(user)
        elif dataset.type == Tweet:
            for tweet in dataset:
                db_tweet = TweetDB()
                db_tweet.parse_tweet_obj(tweet)
        else:
            raise NotSupportedException(f"Dataset type is not supported for processing. Received Type: {dataset.type}")
