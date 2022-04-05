import pickle
from typing import Union, List,Any
from core.dataset import Dataset, DataPoint
from core.exceptions import IllegalTypeException
from twitter.core.tokenizer import TwitterTokenizer
from tweepy.models import User as TweepyUser


class Tweet(DataPoint):
    """
    Class that represents a single tweet.
    """

    def __init__(self, tokenizer: Union[TwitterTokenizer,Any] = None, **parameters: dict):
        super().__init__(**parameters)
        self._text = None
        self.tweet_id = None
        self.retweet_count = None
        self.tweet_created_date = None
        self.like_count = None
        self.search_text = None
        self.user = None
        self.tokenizer = tokenizer if tokenizer is not None else TwitterTokenizer()
        self.processed = False
        self._processed_text = None
        self.db_id = None

    def parse_tweet_obj(self, search_text, tweet):
        self._text = tweet.full_text
        self.tweet_id = tweet.id
        self.retweet_count = tweet.retweet_count
        # self.like_count = tweet.like_count
        self.tweet_created_date = tweet.created_at
        self.search_text = search_text
        self.user = TwitterUser(tweet.user)

    def process(self):
        """
        Runs the text through the tokenizer to preprocess it.
        :return:
        """
        self._processed_text = self.tokenizer.tokenize(self._text)
        self.processed = True

    @property
    def text(self):
        if self.processed:
            return self._processed_text
        else:
            return self._text

    @text.setter
    def text(self, text):
        if self.processed:
            self._text = text
            self._processed_text = self.tokenizer.tokenize(text)
        else:
            self._text = text


class TwitterUser(DataPoint):
    def __init__(self, user: TweepyUser = None, **parameters: dict):
        super().__init__(**parameters)
        self.db_id = None
        self.name = None
        self.description = None
        self.twitter_id = None
        self.twitter_handle = None
        self.followers_count = None
        self.friends_count = None
        self.listed_count = None
        self.statuses_count = None
        self.friends = []
        self.followers = []
        self.twitter_user_created_at = None
        self.created_at = None
        self.twitter_user_object = None
        if user is not None:
            self.parse_twitter_user(user)
            self.twitter_user_object = user

    def parse_twitter_user(self, twitter_user: TweepyUser):
        self.name = twitter_user.name
        try:
            self.twitter_id = twitter_user.id
        except:
            pass
        self.twitter_handle = twitter_user.screen_name
        self.followers_count = twitter_user.followers_count
        self.friends_count = twitter_user.friends_count
        self.listed_count = twitter_user.listed_count
        self.created_at = twitter_user.created_at
        self.description = twitter_user.description
        self.statuses_count = twitter_user.statuses_count
        self.twitter_user_object = twitter_user


class TwitterDataset(Dataset):
    def __init__(self, data_points: Union[List[DataPoint], DataPoint] = None, buffer_size=0, n_workers=None,
                 queue: object = None):
        """
        This class represents the dataset collection for twitter data points. They can be Tweets or Twitter User
        :param data_points: Data Points to initialise the dataset.
        :param buffer_size: Buffer size for preprocessing.
        :param n_workers: Number of workers to preprocess objects
        :param queue:
        """
        super(TwitterDataset, self).__init__(data_points, buffer_size, n_workers, queue)
        self.type = None
        if data_points is not None:
            types = set([type(i) for i in data_points])
        else:
            types = []
        if len(types) > 0:
            raise IllegalTypeException(
                "data_points argument contain more than one type of DataPoint. Each TwitterDataset will support only one type "
                "of DataPoint")
        if len(types) > 0:
            self.type = types.pop()

    def persist(self, file_path: str):
        with open(file_path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def append(self, data: DataPoint, inplace=None):
        if self.type is None:
            self.type = type(data)
        if type(data) != self.type:
            raise IllegalTypeException(
                f"Passing wrong object to dataset. This dataset is configured for only {self.type} objects")
        if inplace is not None:
            print("Warning: inplace argument is not respected for twitter dataset. It is always treated as true")
        self._data.append(data)

    def delete(self, index):
        self._data.pop(index)

    def update(self, index, data: DataPoint):
        if type(data) != self.type:
            raise IllegalTypeException(
                f"Passing wrong object to dataset. This dataset is configured for only {self.type} objects")
        self._data.insert(index, data)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]
