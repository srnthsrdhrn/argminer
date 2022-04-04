from abc import ABC, abstractmethod
from typing import Any

from core.dataset import Dataset, DataPoint


class Crawler(ABC):
    @abstractmethod
    def crawl(self) -> None:
        """
        Main function which is responsible for crawling. The core logic to crawl should go here. Must be implemented by child
        class. The crawled objects will be processed and inserted into the database from within this class itself. Hence it
        doesn't return anything.

        The crawl method should make use of the _create_object method to convert crawled data into objects to be used by other
        objects

        :return: None
        """
        pass

    @abstractmethod
    def _create_object(self, crawl_data: Any) -> DataPoint:
        """
        This function is responsible for converting the crawled data into an object which can be used by the other components.
        :param crawl_data:
        :return:
        """
        pass

    def __del__(self) -> None:
        """
        Destructor for the class. Should take care to clean up all existing crawls and shutdown properly.
        :return: None
        """
        pass

    @abstractmethod
    def _is_useful_entity(self, dataset: Dataset) -> bool:
        """
        Function to decide if entity is useful and further crawling should happen in this direction.
        :param dataset: Dataset object which has the crawl data
        :return: True if crawler needs to proceed along this node. False to stop anymore crawling along this node.
        """
        pass

    def _process_entity(self, dataset: Dataset):
        """
        This method will receive crawled objects as dataset objects. This should take care of processing them and storing them.
        :param dataset: The dataset object. Can be a list of a single entity
        :return:
        """
        pass
