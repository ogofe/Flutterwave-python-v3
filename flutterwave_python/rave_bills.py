import json, requests, copy
import urllib.parse as urlparse
from urllib.parse import urlencode
from flutterwave_python.rave_base import RaveBase
from flutterwave_python.rave_misc import checkIfParametersAreComplete
from flutterwave_python.rave_exceptions import ServerError, IncompleteCardDetailsError, BillCreationError, BillStatusError

class Bills(RaveBase):
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        self.headers = {
            'content-type' : 'application/json',
            'authorization' : 'Bearer ' + secretKey,
        }
        super(Bills, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)

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

    def _handleCreateResponse(self, response, details):
        responseJson = self._preliminaryResponseChecks(response, BillCreationError, details["customer"])

        if responseJson["status"] == "success":
            return {"error": False, "id": responseJson["data"].get("id", None), "data": responseJson["data"] }

        else:
            raise BillCreationError({"error": True, "data": responseJson["data"]})

    def _handleBillStatusRequests(self, type, endpoint, method, data=None):
        
        #check if resposnse is a post response
        if method == 'GET':
            if data == None:
                response = requests.get(endpoint, headers=self.headers)
            else:
                response = requests.get(endpoint, headers=self.headers, data=json.dumps(data))
        elif method == 'POST':
            if data == None:
                response = requests.post(endpoint, headers=self.headers)
            else:
                response = requests.post(endpoint, headers=self.headers, data=json.dumps(data))
        elif method == 'PUT':
            response = requests.put(endpoint, headers=self.headers, data=json.dumps(data))
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
            raise BillStatusError(type, {"error": True, "returnedData": responseJson })


    #function to create a Bill
    #Params: details - a dict containing service, service_method, service_version, service_channel and service_payload
    def create(self, details):
        # Performing shallow copy of planDetails to avoid public exposing payload with secret key
        # details = copy.copy(details)
        # details.update({"seckey": self._getSecretKey()})

        requiredParameters = ["country", "customer", "amount", "recurrence", "type"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpoint = self._baseUrl + self._endpointMap["bills"]["create"]
        response = requests.post(endpoint, headers=self.headers, data=json.dumps(details))
        return self._handleCreateResponse(response, details)

    def bulk(self, details):
        requiredParameters = ["bulk_reference", "callback_url", "bulk_data"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpoint = self._baseUrl + self._endpointMap["bills"]["bulk"]
        data = details
        method = 'POST'
        return self._handleBillStatusRequests("bulk-bill", endpoint, method, data = data)

    def getStatus(self, tx_ref):
        endpoint = self._baseUrl + self._endpointMap["bills"]["get-status"] + "/" + str(tx_ref)
        method = 'GET'
        return self._handleBillStatusRequests("bulk-bill", endpoint, method, data = None)

    def update(self, details):
        requiredParameters = ["order_id", "amount"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpoint = self._baseUrl + self._endpointMap["bills"]["update"] + "/" + details["order_id"]
        data = details
        method = 'PUT'
        return self._handleBillStatusRequests("bulk-bill", endpoint, method, data = data)

    def billCategory(self):
        endpoint = self._baseUrl + self._endpointMap["bills"]["bill-category"]
        # data = details
        method = 'GET'
        return self._handleBillStatusRequests("bill-category", endpoint, method, data = None)

    #pass phone number without internation number format i.e. +234
    def validateService(self, details):
        requiredParameters = ["item_code", "code", "customer"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpt = self._baseUrl + self._endpointMap["bills"]["bill-service"] + "/" + details["item_code"] + "/validate"
        data = details

        url_parts = list(urlparse.urlparse(endpt))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(details)

        url_parts[4] = urlencode(query)

        endpoint = urlparse.urlunparse(url_parts)
        method = 'GET'
        return self._handleBillStatusRequests("validate-service", endpoint, method, data = data)

    def allBillers(self):
        endpoint = self._baseUrl + self._endpointMap["bills"]["all"]
        # data = details
        method = 'GET'
        return self._handleBillStatusRequests("all-categories", endpoint, method, data = None)

    def amount(self, biller_code, product_id):
        endpoint = self._baseUrl + self._endpointMap["bills"]["all"] + "/" + str(biller_code) + "/products/" + str(product_id)
        # data = details
        method = 'GET'
        return self._handleBillStatusRequests("get-bill-amount", endpoint, method, data = None)

    def createOrder(self, details):
        requiredParameters = ["item_code", "code", "customer", "fields"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpoint = self._baseUrl + self._endpointMap["bills"]["all"] + "/" + details["item_code"] + "/products/" + details["code"] + "/orders" 
        data = details
        method = 'POST'
        return self._handleBillStatusRequests("get-bill-amount", endpoint, method, data = data)

    def all(self, details):
        requiredParameters = ["from", "to"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpt = self._baseUrl + self._endpointMap["bills"]["create"]
        data = details
        
        url_parts = list(urlparse.urlparse(endpt))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(details)

        url_parts[4] = urlencode(query)

        endpoint = urlparse.urlunparse(url_parts)
        method = 'GET'
        return self._handleBillStatusRequests("get_all-bills", endpoint, method, data = data)

    def allProducts(self, biller_code):
        endpoint = self._baseUrl + self._endpointMap["bills"]["all"] + "/" + str(biller_code) + "/products"
        # data = details
        method = 'GET'
        return self._handleBillStatusRequests("all-categories", endpoint, method, data = None)
