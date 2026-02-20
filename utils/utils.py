import re
import time


def is_email_valid(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    return bool(re.match(pattern, email))


def make_slug(title: str) -> str:
    title = title.replace(' ', '-')
    title = title.lower()
    time_in_seconds = int(time.time())

    return f'{title}-{time_in_seconds}'
