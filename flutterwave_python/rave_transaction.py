import requests, json, copy
import urllib.parse as urlparse
from urllib.parse import urlencode
from flutterwave_python.rave_base import RaveBase
from flutterwave_python.rave_misc import checkIfParametersAreComplete, generateTransactionReference, checkTransferParameters
from flutterwave_python.rave_exceptions import InitiateTransferError, ServerError, TransferFetchError, IncompletePaymentDetailsError


class Transaction(RaveBase):
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        super(Transaction, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)
    
    def _preliminaryResponseChecks(self, response, TypeOfErrorToRaise, reference):
        # Check if we can obtain a json
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "reference": reference, "errMsg": response})

        # Check if the response contains data parameter
        if not responseJson.get("data", None):
            raise TypeOfErrorToRaise({"error": True, "reference": reference, "errMsg": responseJson.get("message", "Server is down")})
        
        # Check if it is returning a 200
        if not response.ok:
            errMsg = responseJson["data"].get("message", None)
            raise TypeOfErrorToRaise({"error": True, "errMsg": errMsg})

        return responseJson


    def _handleInitiateResponse(self, response, transferDetails):
        responseJson = self._preliminaryResponseChecks(response, InitiateTransferError, transferDetails["reference"])
        
        if responseJson["status"] == "success":
            return {"error": False, "id": responseJson["data"].get("id", None), "data": responseJson["data"]}
        
        else:
            raise InitiateTransferError({"error": True, "data": responseJson["data"]})

    # def _handleBulkResponse(self, response, bulkDetails):
    #     responseJson = self._preliminaryResponseChecks(response, InitiateTransferError, None)

    #     if responseJson["status"] == "success":
    #         return {"error": False, "status": responseJson["status"], "message":responseJson["message"], "id": responseJson["data"].get("id", None), "data": responseJson["data"]}
    #     else:
    #         raise InitiateTransferError({"error": True, "data": responseJson["data"]})

            
    # def initiate(self, transferDetails):
    #     # Performing shallow copy of transferDetails to avoid public exposing payload with secret key
    #     transferDetails = copy.copy(transferDetails)

    #     # adding reference if not already included
    #     if not ("reference" in transferDetails):
    #         transferDetails.update({"reference": generateTransactionReference()})
    #     transferDetails.update({"seckey": self._getSecretKey()})

    #     # These are the parameters required to initiate a transfer
    #     requiredParameters = ["amount", "currency","account_bank", "account_number"]
    #     checkIfParametersAreComplete(requiredParameters, transferDetails)
    #     checkTransferParameters(requiredParameters, transferDetails)

    #     # Collating request headers
    #     headers = {
    #         'content-type': 'application/json',
    #         'authorization' : 'Bearer ' + self._getSecretKey(),
    #     }
        
    #     endpoint = self._baseUrl + self._endpointMap["transfer"]["initiate"]
    #     response = requests.post(endpoint, headers=headers, data=json.dumps(transferDetails))
    #     return self._handleInitiateResponse(response, transferDetails)



    # def bulk(self, bulkDetails):
        
    #     bulkDetails = copy.copy(bulkDetails)
    #     # Collating request headers
    #     headers = {
    #         'content-type': 'application/json',
    #         'authorization' : 'Bearer ' + self._getSecretKey(),
    #     }

    #     # bulkDetails.update({"seckey": self._getSecretKey()})

    #     requiredParameters = ["bulk_data"]
    #     checkIfParametersAreComplete(requiredParameters, bulkDetails)
    #     checkTransferParameters(requiredParameters, bulkDetails)
    #     endpoint = self._baseUrl + self._endpointMap["transfer"]["bulk"]
        
    #     # Collating request headers
    #     headers = {
    #         'content-type': 'application/json',
    #         'authorization' : 'Bearer ' + self._getSecretKey(),
    #     }
    #     response = requests.post(endpoint, headers=headers, data=json.dumps(bulkDetails))
    #     return self._handleBulkResponse(response, bulkDetails)

    
    # This makes and handles all requests pertaining to the status of your transfer or account
    def _handleTransferStatusRequests(self, endpoint, method, data=None):
        # Request headers
        headers = {
            'content-type': 'application/json',
            'authorization' : 'Bearer ' + self._getSecretKey(),
        }

        #check if response is a post response
        if method == 'GET':
            if data == None:
                response = requests.get(endpoint, headers=headers)
            else:
                response = requests.get(endpoint, headers=headers, data=json.dumps(data))
        elif method == 'POST':
            response = requests.post(endpoint, headers=headers)
        elif method == 'PUT':
            response = requests.put(endpoint, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(endpoint, headers=headers, data=json.dumps(data))
        else:
            response = requests.delete(endpoint, headers=headers, data=json.dumps(data))

        # Checks if it can be parsed to json
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "errMsg": response.text })

        # Checks if it returns a 2xx code
        if response.ok:
            return {"error": False, "returnedData": responseJson}
        else:
            raise TransferFetchError({"error": True, "returnedData": responseJson })

    # Not elegant but supports python 2 and 3
    # def fetch(self, reference=None):
    #     endpoint = self._baseUrl + self._endpointMap["transfer"]["fetch"] + "?seckey="+self._getSecretKey()+'&reference='+str(reference)
    #     return self._handleTransferStatusRequests(endpoint)

    def all(self, details):
        endpt = self._baseUrl + self._endpointMap["transaction"]["all"] + "?"
        data = details

        #parse query params
        url_parts = list(urlparse.urlparse(endpt))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(details)
        url_parts[4] = urlencode(query)
        endpoint = urlparse.urlunparse(url_parts)

        method = 'GET'

        return self._handleTransferStatusRequests(endpoint, method, data = data)

    def getFee(self, details):
        requiredParameters = ["amount"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpt = self._baseUrl + self._endpointMap["transaction"]["fee"] + "?"
        data = details

        #parse query params
        url_parts = list(urlparse.urlparse(endpt))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(details)
        url_parts[4] = urlencode(query)
        endpoint = urlparse.urlunparse(url_parts)

        method = 'GET'
        
        return self._handleTransferStatusRequests(endpoint, method, data = data)
        
    def resendHook(self, tx_ref):
        endpoint =  self._baseUrl + self._endpointMap["transaction"]["resend_webhook"] + "/" + str(tx_ref) + "/resend-hook"
        method = 'POST'
        return self._handleTransferStatusRequests(endpoint, method, data = None)

    #pass data.id as tranx_id
    def timeline(self, tranx_id):
        endpoint =  self._baseUrl + self._endpointMap["transaction"]["timeline"] + "/" + str(tranx_id) + "/events"
        method = 'GET'
        return self._handleTransferStatusRequests(endpoint, method)

    # def accountResolve(self, details):
    #     endpoint = self._baseUrl + self._endpointMap["transfer"]["account-resolve"]
    #     data = details
    #     return self._handleTransferStatusRequests(endpoint, data = data)

    # def bvnResolve(self, details):
    #     endpoint = self._baseUrl + self._endpointMap["transfer"]["bvn"]
    #     data = details
    #     return self._handleTransferStatusRequests(endpoint, data = data)

