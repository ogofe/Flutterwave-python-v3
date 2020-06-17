import json, requests, copy
import urllib.parse as urlparse
from urllib.parse import urlencode
from flutterwave_python.rave_base import RaveBase
from flutterwave_python.rave_misc import checkIfParametersAreComplete
from flutterwave_python.rave_exceptions import ServerError, IncompleteCardDetailsError, CardCreationError, CardStatusError

class Settlement(RaveBase):
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        self.headers = {
            'content-type' : 'application/json',
            'authorization' : 'Bearer ' + secretKey,
        }
        super(Settlement, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)

    def _preliminaryResponseChecks(self, response, TypeOfErrorToRaise, name):
        #check if we can get json
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "name": name, "errMsg": response})

        #check for data parameter in response 
        if not responseJson.get("data", None):
            raise TypeOfErrorToRaise({"error": True, "name": name, "errMsg": responseJson.get("message", "Server is down")})

        #check for 200 response
        if not response.ok:
            errMsg = response["data"].get("message", None)
            raise TypeOfErrorToRaise({"error": True, "errMsg": errMsg})

        return responseJson

    # def _handleCreateResponse(self, response, details):
    #     responseJson = self._preliminaryResponseChecks(response, CardCreationError, details["billing_name"])

    #     if responseJson["status"] == "success":
    #         return {"error": False, "id": responseJson["data"].get("id", None), "data": responseJson["data"] }

    #     else:
    #         raise CardCreationError({"error": True, "data": responseJson["data"]})

    def _handleCardStatusRequests(self, type, endpoint, method, data=None):
        
        #check if response is a post response
        if method == 'GET':
            if data == None:
                response = requests.get(endpoint, headers=self.headers)
            else:
                response = requests.get(endpoint, headers=self.headers, data=json.dumps(data))
        elif method == 'POST':
            response = requests.post(endpoint, headers=self.headers, data=json.dumps(data))
        elif method == 'PUT':
            response = requests.put(endpoint, headers=self.headers)
        elif method == 'PATCH':
            response = requests.patch(endpoint, headers=self.headers, data=json.dumps(data))
        else:
            response = requests.delete(endpoint, headers=self.headers, data=json.dumps(data))
        
        #check if it can be parsed to JSON
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "errMsg": response.text})

        if response.ok:
            return {"error": False, "returnedData": responseJson}
        else:
            raise CardStatusError(type, {"error": True, "returnedData": responseJson })


    #function to list and fetch settlements
    #Params: details - a dict containing service, service_method, service_version, service_channel and service_payload
    def all(self):
        endpoint = self._baseUrl + self._endpointMap["settlements"]["list"]
        method = 'GET'
        return self._handleCardStatusRequests("list-all-settlements", endpoint, method, data = None)

    def fetch(self, settlement_id):
        endpoint = self._baseUrl + self._endpointMap["settlements"]["fetch"] + "/" + str(settlement_id) 
        # data = details
        # url_parts = list(urlparse.urlparse(endpt))
        # query = dict(urlparse.parse_qsl(url_parts[4]))
        # query.update(details)
        # url_parts[4] = urlencode(query)
        # endpoint = urlparse.urlunparse(url_parts)
        method = 'GET'
        return self._handleCardStatusRequests("fetch-settlement", endpoint, method, data = None)