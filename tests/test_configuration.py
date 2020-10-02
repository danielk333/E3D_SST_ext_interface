import pathlib 

#requests we should handle
HANDLE_REQUESTS = {
    'CreateSensorRequestType': 'CreateSensorResponseType',
    'UpdateSensorRequestType': 'UpdateSensorResponseType',
    'DeleteSensorRequestType': 'DeleteSensorResponseType',
    'planningRequestStatusUpdatedRequest': '',
    'SubmitObservationDataRequestType': 'SubmitObservationDataResponseType',
    'RetrieveCurrentEphemerisRequest': 'retrieveCurrentEphemerisResponse',
    'SetActiveSensorsRequestType': 'SetActiveSensorsResponseType',
}

#requests we should send
SEND_REQUESTS = {
    'CreateSensorRequestType': 'CreateSensorResponseType',
    'UpdateSensorRequestType': 'UpdateSensorResponseType',
    'DeleteSensorRequestType': 'DeleteSensorResponseType',
    'planningRequestStatusUpdatedRequest': '',
    'SubmitObservationDataRequestType': 'SubmitObservationDataResponseType',
    'RetrieveCurrentEphemerisRequest': 'retrieveCurrentEphemerisResponse',
    'SetActiveSensorsRequestType': 'SetActiveSensorsResponseType',
}

MOCK_ESA_HOST = 'localhost'
MOCK_ESA_PORT = 32770

SST_HOST = 'localhost'
SST_PORT = 32769

HTTP_200 = '200 OK'
HTTP_404 = '404 Not Found'

ROOT = pathlib.Path(__file__)