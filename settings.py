import os

TEMPLATE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'templates/')
DEBUG = os.getenv('SERVER_SOFTWARE').split('/')[0] == "Development" if os.getenv('SERVER_SOFTWARE') else False
