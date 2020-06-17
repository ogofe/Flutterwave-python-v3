#updated for v3
import json, requests, copy
import urllib.parse as urlparse
from urllib.parse import urlencode
from flutterwave_python.rave_base import RaveBase
from flutterwave_python.rave_misc import checkIfParametersAreComplete
from flutterwave_python.rave_exceptions import ServerError, IncompleteCardDetailsError, CardCreationError, CardStatusError

class VirtualCard(RaveBase):
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        self.headers = {
            'content-type' : 'application/json',
            'authorization' : 'Bearer ' + secretKey,
        }
        super(VirtualCard, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)

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

    def _handleCreateResponse(self, response, virtual_cardDetails):
        responseJson = self._preliminaryResponseChecks(response, CardCreationError, virtual_cardDetails["billing_name"])

        if responseJson["status"] == "success":
            return {"error": False, "id": responseJson["data"].get("id", None), "data": responseJson["data"] }

        else:
            raise CardCreationError({"error": True, "data": responseJson["data"]})

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



    #function to create a virtual card 
    #Params: virtual_cardDetails - a dict containing currency, amount, billing_name, billing_address, billing_city, billing_state, billing_postal_code, billing_country
    # def create(self, virtual_cardDetails):
    #     virtual_cardDetails = copy.copy(virtual_cardDetails)
    #     virtual_cardDetails.update({"seckey": self._getSecretKey()})
        
    #     requiredParameters = ["currency", "amount", "billing_name", "billing_address", "billing_city", "billing_state", "billing_postal_code", "billing_country"]
    #     checkIfParametersAreComplete(requiredParameters, virtual_cardDetails)

    #     endpoint = self._baseUrl + self._endpointMap["virtual_card"]["create"]
    #     response = requests.post(endpoint, headers=self.headers, data=json.dumps(virtual_cardDetails))
    #     return self._handleCreateResponse(response, virtual_cardDetails)

    def create(self, virtual_cardDetails):
        requiredParameters = ["currency", "amount", "billing_name", "billing_address", "billing_city", "billing_state", "billing_postal_code", "billing_country"]
        checkIfParametersAreComplete(requiredParameters, virtual_cardDetails)

        endpoint = self._baseUrl + self._endpointMap["virtual_card"]["create"]
        response = requests.post(endpoint, headers=self.headers, data=json.dumps(virtual_cardDetails))
        return self._handleCreateResponse(response, virtual_cardDetails)

    #gets all virtual cards connected to a merchant's account
    def all(self):
        endpoint = self._baseUrl + self._endpointMap["virtual_card"]["list"]
        method = 'GET'
        return self._handleCardStatusRequests("list-all-cards", endpoint, method, data = None)

    #permanently deletes a card with specified id 
    def terminate(self, card_id):
        if not card_id:
            return "Card id was not supplied. Kindly supply one"
        endpoint = self._baseUrl + self._endpointMap["virtual_card"]["terminate"] + "/" + str(card_id) + "/terminate"
        method = 'PUT'
        return self._handleCardStatusRequests("terminate-virtual-card", endpoint, method)

    #fetches Card details and transactions for a cars with specified id
    def get(self, card_id):
        endpoint = self._baseUrl + self._endpointMap["virtual_card"]["get"] + "/" + str(card_id)
        method = 'GET'
        return self._handleCardStatusRequests("Get-card-details", endpoint, method, data = None)

    #temporarily suspends the use of card
    def block(self, card_id):
        endpoint = self._baseUrl + self._endpointMap["virtual_card"]["freeze"] + "/" + str(card_id) + "/status/block"
        method = 'PUT'
        return self._handleCardStatusRequests("block-virtual-account", endpoint, method)

    #reverses the freeze card operation
    def unblock(self, card_id):
        endpoint = self._baseUrl + self._endpointMap["virtual_card"]["unfreeze"] + "/" + str(card_id) + "/status/unblock"
        method = 'PUT'
        return self._handleCardStatusRequests("unblock-virtual-account", endpoint, method)

    #funds a card with specified balance for online transactions
    def fund(self, details):
        requiredParameters = ["id", "amount", "debit_currency"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpoint = self._baseUrl + self._endpointMap["virtual_card"]["fund"] + "/" + details['id'] + "/fund"
        data = details
        method = 'POST'
        return self._handleCardStatusRequests("fund-virtual-card", endpoint, method, data=data)

    #withdraws funds from Virtual card. Withdrawn funds are added to Rave Balance
    def withdraw(self, details):
        requiredParameters = ["id", "amount"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpoint = self._baseUrl + self._endpointMap["virtual_card"]["withdraw"] + "/" + details['id'] + "/withdraw"
        data = details
        method = 'POST'
        return self._handleCardStatusRequests("withdraw-card-funds", endpoint, method, data=data)

    def transactions(self, details, card_id):
        requiredParameters = ["from", "to", "index", "size"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpt = self._baseUrl + self._endpointMap["virtual_card"]["transactions"] + "/" + str(card_id) + "/transactions?"
        data = details

        url_parts = list(urlparse.urlparse(endpt))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(details)

        url_parts[4] = urlencode(query)

        endpoint = urlparse.urlunparse(url_parts)
        method = 'GET'
        return self._handleCardStatusRequests("get-virtual-card-transactions", endpoint, method, data=data)
