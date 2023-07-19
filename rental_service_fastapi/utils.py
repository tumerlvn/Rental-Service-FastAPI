from typing import Annotated
from fastapi import Depends
from datetime import datetime

class CommonQueryParams:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit


SkipLimit = Annotated[CommonQueryParams, Depends()]


def compare_hour_to_diff_time(time_from: datetime, time_to: datetime, h: int = 1):
    diff = time_to - time_from
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    return hours > h