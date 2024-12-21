from enum import Enum


class Order(Enum):
  market = 0
  limit = 1
  fillOrKill = 2
  cancel = 3


