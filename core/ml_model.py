from abc import ABC, abstractmethod

from core.dataset import Dataset, DataPoint


class MLModel(ABC):
    def __init__(self):
        """
        This class acts as base class for all ML Model classes used in this project. This will contain the basic contracts
        that the other components in the system rely on. When inheriting this class make sure to properly implement all the
        relevant functions for your model.
        """

    @abstractmethod
    def train(self, training_data: Dataset):
        """
        Will take in a Dataset object. Iterate over it and train a model.
        :param training_data: The dataset object or object of any class that inherits the Dataset class.
        :return: None
        """

    @abstractmethod
    def predict(self, x: DataPoint) -> DataPoint:
        """
        The prediction wil happen on a DataPoint instance only. Returns the prediction back as a DataPoint instance.
        :param x: datapoint instance
        :return:
        """

    @abstractmethod
    def persist(self, file_path: str):
        """
        Save the ML Model to the specified file path. If there are more than one files comprising your ml model, try to zip all
        the files together.
        :param file_path: The file path to save the ml model.
        :return:
        """

    @abstractmethod
    def load(self, file_path: str):
        """
        Load the saved ml model. If you had to zip your files during persisting, make sure you unzip it in a tmp directory
        before loading
        :param file_path:
        :return:
        """


class EconomicTextClassifier(MLModel):
    def __init__(self):
        """
        This model is used to classify a text as something related to stocks and economy or not
        """
        super(EconomicTextClassifier, self).__init__()

    def train(self, training_data: Dataset):
        pass

    def predict(self, x: DataPoint) -> DataPoint:
        pass

    def persist(self, file_path: str):
        pass

    def load(self, file_path: str):
        pass
