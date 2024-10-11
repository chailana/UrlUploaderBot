import os


class Config(object):
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

    APP_ID = int(os.environ.get("APP_ID", 12345))

    API_HASH = os.environ.get("API_HASH", "")

    STRING_SESSION = os.environ.get("STRING_SESSION", "1BVtsOH0Bu0SmIIde8ZsdV0GV1SGCnLtko8YvNwKJgavF3i93UmAVH6_EYtPd_THQ3zp3C4JIK3KwnRydJvVFMzEkfkiLMqes_yVJTyxobFmSvv7zrLIEHY75uCmLPhjEDhyM688KM1LwceYRwvIJI8-BFoIvFrMR5fTzBIQPF1J6dxBzIxRIEum7Jm6hwYS8mP7kvUG5C8OuaqXkEsYpplxgvfr8yj4U6hKNx19tJZggphG5PIU6KWwMPZYR-h8ymVmMXTRjov-Z8IcrHXJFjT17exDh9ax7gcLRytj1fH1kABdzbierblnDF31iM5DwIy0s5D4PlWM1nyaKw58UODuY-jIFnUc=")
