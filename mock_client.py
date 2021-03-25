import pathlib

from suds.client import Client
from suds.cache import ObjectCache

client = Client('http://localhost:8000/test.wsdl', cache=None)

out = client.service.say_hello('Daniel', 10)
print(out)