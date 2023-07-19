from typing import List, Optional
from fastapi import Request
import re

regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

class UserCreateForm:
    def __init__(self, username: str, email: str, password: str):
        self.errors: List = []
        self.username = username
        self.email = email
        self.password = password

    def is_valid(self):
        if not self.username or not len(self.username) > 3:
            self.errors.append("Username should be > 3 chars")
        if not self.email or not (re.search(regex,self.email)):
            self.errors.append("Wrong email format")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("Password must be >= 4 chars")
        if not self.errors:
            return True
        return False