import pathlib

from suds.client import Client
from suds.cache import ObjectCache
from suds.xsd.doctor import Import, ImportDoctor

# imp=Import('http://www.w3.org/2001/XMLSchema',location='http://www.w3.org/2001/XMLSchema.xsd')
# , doctor=ImportDoctor(imp)

# client = Client(
#     'http://localhost:8000/hello/hello.wsdl',
#     location='http://localhost:8000/hello/hello',
#     cache=None,
# )
# out = client.service.say_hello('Daniel', 10)
# print(out)

# client = Client(
#     'http://localhost:8000/SST_Core/SSIM/v2.0/SensorSimulatorService/Wsdl/SensorSimulatorService.wsdl',
#     location='http://localhost:8000/SST_Core/SSIM/v2.0/SensorSimulatorService/Wsdl/SensorSimulatorService',
#     cache=None,
# )

# client = Client(
#     'http://localhost:8000/test1/test.wsdl',
#     location='http://localhost:8000/test1/test',
#     cache=None,
# )

client = Client(
    'http://localhost:8000/test2/test.wsdl',
    location='http://localhost:8000/test2/test',
    cache=None,
)


