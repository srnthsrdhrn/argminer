from abc import ABC, abstractmethod
from multiprocessing import cpu_count
from typing import List, Union


class DataPoint(ABC):
    def __init__(self, **parameters: dict):
        """
        DataPoint class represents one unit of a dataset class. This is specifically made so that data points can be created in
        isolation and clubbed together as a dataset object
        """
        for name, param in parameters.items():
            self.__setattr__(name, param)
        self._is_processed = False

    def process(self):
        """
        This method should do the preprocessing operations necessary for this particular datapoint.
        :return:
        """
        pass

    def update(self, **parameters: dict):
        """
        This function is used to update the parameters of a Datapoint object. It forms a union of the existing parameters and
        the old parameters, and replaces old parameters wherever conflict occurs.
        :param parameters: new parameters to update.
        :return:
        """
        for name, param in parameters.items():
            self.__setattr__(name, param)


class Dataset(ABC):
    def __init__(self, data_points: Union[List[DataPoint], DataPoint] = None, buffer_size=0, n_workers=None,
                 queue: object = None):
        """
        This class acts as a superclass for all dataset classes. Any form of data expressed as a dataset class should be
        compatible across the system. This class should respect the DataPoint class as valid arguments to respective functions.
        The core functions of this class are:
        1. Load Dataset
            Load from File
            Load from s3
        2. Preprocess the dataset
        3. Allow access to the dataset across the system.
        This class can contain a single data point or a list of data points.
        :type data_points: This is the initial set of data points to create the dataset. It can either be a list of data points
        or a single data point
        :param buffer_size: When the buffer size is set to 0, this class allows random access to the data. When buffer size is
        greater than 0, the class utilizes the workers to preprocess the data before hand and keep it ready
        :param n_workers: THe number of workers to use to preprocess the data. A value of -1 will use all cpu cores as workers
        :param queue: The queue object to keep processed items.  It must be a priority queue. This is just there so that
        external queue can be supported in future. Its better not to override it unless you know what you are doing.

        Todo: Implement queue and preprocessing of data with workers

        As of now the data is just stored as a list in the _data object.
        """
        self.buffer_size = buffer_size
        self.n_workers = n_workers if n_workers != -1 else cpu_count()
        self.queue = queue
        if data_points is not None:
            self._data = data_points if type(data_points) == list else [data_points]
        else:
            self._data = []

    @abstractmethod
    def persist(self, file_path: str):
        """
        Function to save the dataset down to disk. This function should store the raw dataset and not the processed one. Try
        not to pickle everything as a class. Store the class parameters as json, and copy the dataset into the folder,
        and try to zip it
        :param file_path: The file path to save the object
        :return:
        """
        pass

    @staticmethod
    def load(file_path):
        """
        Load the saved dataset object. Extract it from the zip file and store the raw data in a folder to be used.
        :param file_path: The file path to retrieve the object
        :return:
        """
        pass

    @abstractmethod
    def append(self, data: DataPoint, inplace=True):
        """
        Append another Dataset object into the current one and return the new one.
        :return:
        """
        pass

    @abstractmethod
    def delete(self, index):
        """
        Delete the element at the specified index
        :param index: The index to delete
        :return:
        """
        pass

    @abstractmethod
    def update(self, index, data: DataPoint):
        """
        Update an element in the dataset class with another datapoint. The object at the index will be replaced with the
        datapoint object passed
        :param index: The index to update
        :param data: The DataPoint object to update.
        :return:
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """
        Override this function to provide an efficient way to find the length of the dataset.
        :return: Length of the dataset
        """

    @abstractmethod
    def __getitem__(self, index):
        """
        The dataset class should implement the get_item function to retrieve the data. Try to dynamically generate the dataset
        instead of preloading everything. This function should also have support for slicing operations.
        :param index: The index of the dataset to retrieve
        :return:
        """
        pass
