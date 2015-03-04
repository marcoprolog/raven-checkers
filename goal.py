from abc import ABCMeta, abstractmethod


class Goal:
    __metaclass__ = ABCMeta

    INACTIVE = 0
    ACTIVE = 1
    COMPLETED = 2
    FAILED = 3

    def __init__(self, owner):
        self.owner = owner
        self.status = self.INACTIVE

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def terminate(self):
        pass

    def handle_message(self, msg):
        return False

    def reactivate_if_failed(self):
        if self.status == self.FAILED:
            self.status = self.INACTIVE

    def activate_if_inactive(self):
        if self.status == self.INACTIVE:
            self.status = self.ACTIVE
