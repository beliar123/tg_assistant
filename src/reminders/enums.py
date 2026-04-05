from enum import Enum


class EventRepeatInterval(Enum):
    DAILY = "ежедневно"
    WEEKLY = "еженедельно"
    MONTHLY = "ежемесячно"
    SIXMONTH = "раз в полгода"
    YEARLY = "ежегодно"
