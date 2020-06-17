import json, requests, copy
from flutterwave_python.rave_base import RaveBase
from flutterwave_python.rave_misc import checkIfParametersAreComplete
from flutterwave_python.rave_exceptions import ServerError, IncompleteAccountDetailsError, AccountCreationError, AccountStatusError

class VirtualAccount(RaveBase):
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        self.headers = {
            'content-type' : 'application/json',
            'authorization' : 'Bearer ' + secretKey,
        }
        super(VirtualAccount, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)

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

    def _handleCreateResponse(self, response, accountDetails):
        responseJson = self._preliminaryResponseChecks(response, AccountCreationError, accountDetails["email"])

        if responseJson["status"] == "success":
            return {"error": False, "id": responseJson["data"].get("id", None), "data": responseJson["data"] }

        else:
            raise AccountCreationError({"error": True, "data": responseJson["data"]})

    def _handleAccountStatusRequests(self, type, endpoint, method, data=None):
        
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
            raise AccountStatusError(type, {"error": True, "returnedData": responseJson })


    #function to create a virtual card 
    #Params: cardDetails - a dict containing email, is_permanent, frequency, duration, narration
    def create(self, accountDetails):
        requiredParameters = ["email", "duration", "frequency", "tx_ref", "amount"]
        checkIfParametersAreComplete(requiredParameters, accountDetails)

        endpoint = self._baseUrl + self._endpointMap["virtual_account"]["create"]
        response = requests.post(endpoint, headers=self.headers, data=json.dumps(accountDetails))
        return self._handleCreateResponse(response, accountDetails)

    def bulk(self, details):
        endpoint = self._baseUrl + self._endpointMap["virtual_account"]["bulk_account"]
        method = 'POST'
        return self._handleAccountStatusRequests("create-bulk-accounts", endpoint, method, data = None)

    def get(self, order_ref):
        endpoint = self._baseUrl + self._endpointMap["virtual_account"]["get"] + "/" + str(order_ref)
        method = 'GET'
        return self._handleAccountStatusRequests("get-account-details", endpoint, method, data = None)

    def getBulk(self, batch_id):
        endpoint = self._baseUrl + self._endpointMap["virtual_account"]["get_bulk_account"] + "/" + str(batch_id)
        method = 'GET'
        return self._handleAccountStatusRequests("get-bulk-account-details", endpoint, method, data = None)