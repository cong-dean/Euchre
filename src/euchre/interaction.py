import abc
import random


class AbstractUserInterface(abc.ABC):
    @abc.abstractmethod
    def display(self):
        raise NotImplementedError

    @abc.abstractmethod
    def question(self, text, datatype=str, options=None):
        raise NotImplementedError


class ConsoleUI(AbstractUserInterface):
    def display(self, text):
        print(text)

    def question(self, text, datatype=str, options=None):
        response = None
        while response is None:
            try:
                response = datatype(input(text + " "))
            except ValueError:
                self.display("Not a valid response")
            if options is not None and response not in options:
                self.display("Choose a valid option, please")

        return response


class NullUI(AbstractUserInterface):
    def display(self, text):
        pass

    def question(self, text, datatype=str, options=None):
        pass


class FakeUI(AbstractUserInterface):

    _log = []

    def display(self, text):
        self._log.append(text)

    def question(self, text, datatype=str, options=None):
        if options is not None:
            return random.choice(list(options))
        return datatype("0")
