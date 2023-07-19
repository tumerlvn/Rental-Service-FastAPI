import enum

class RequestApprovedState(enum.Enum):
    yes = "YES"
    no = "NO"
    not_yet = "NOT YET"


class Grade(enum.Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5