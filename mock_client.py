import sys
import pathlib

from suds.client import Client
from suds.cache import ObjectCache
from suds.xsd.doctor import Import, ImportDoctor

#Possible solutions
# imp=Import('http://www.w3.org/2001/XMLSchema',location='http://www.w3.org/2001/XMLSchema.xsd')
# , doctor=ImportDoctor(imp)

tests = {}

def test0():
    client = Client(
        'http://localhost:8000/hello/hello.wsdl',
        location='http://localhost:8000/hello/hello',
        cache=None,
    )
    print(client)

    out = client.service.say_hello('Daniel', 10)
    print(out)
tests[0] = test0


def test1():
    client = Client(
        'http://localhost:8000/SST_Core/SSIM/v2.0/SensorSimulatorService/Wsdl/SensorSimulatorService.wsdl',
        location='http://localhost:8000/SST_Core/SSIM/v2.0/SensorSimulatorService/Wsdl/SensorSimulatorService',
        cache=None,
    )
    print(client)
tests[1] = test1


def test2():
    client = Client(
        'http://localhost:8000/test1/test.wsdl',
        location='http://localhost:8000/test1/test',
        cache=None,
    )
    print(client)
tests[2] = test2


def test3():
    client = Client(
        'http://localhost:8000/test2/test.wsdl',
        location='http://localhost:8000/test2/test',
        cache=None,
    )
    print(client)
tests[3] = test3

def test4():
    client = Client(
        'http://localhost:8000/test3/test.wsdl',
        location='http://localhost:8000/test3/test',
        cache=None,
    )
    print(client)

    out = client.service.get_tdm(5464214)
    print(out)
tests[4] = test4


if __name__=='__main__':

    if len(sys.argv) < 1:
        test_id = 0
    else:
        test_id = int(sys.argv[1])

    _test = tests[test_id]
    print(f'Running test {test_id}')
    _test()
    