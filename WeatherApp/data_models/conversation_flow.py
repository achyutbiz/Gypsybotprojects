
from enum import Enum


class Question(Enum):
    NAME = 1
    EMAIL = 2
    MOBILENUMBER = 3
    CITYNAME = 4
    NONE = 5


class ConversationFlow:
    def __init__(
        self, last_question_asked: Question = Question.NONE,
    ):
        self.last_question_asked = last_question_asked
