import requests, json, copy
from flutterwave_python.rave_base import RaveBase
from flutterwave_python.rave_misc import checkIfParametersAreComplete, generateTransactionReference
from flutterwave_python.rave_exceptions import  ServerError, IncompletePaymentDetailsError, PlanCreationError, PlanStatusError

class Subscriptions(RaveBase) :
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        self.headers = {
            'content-type': 'application/json',
            'authorization' : 'Bearer ' + secretKey,
        }
        super(Subscriptions, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)
    
    def _preliminaryResponseChecks(self, response, TypeOfErrorToRaise, name):
        # Check if we can obtain a json
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "name": name, "errMsg": response})

        # Check if the response contains data parameter
        if not responseJson.get("data", None):
            raise TypeOfErrorToRaise({"error": True, "name": name, "errMsg": responseJson.get("message", "Server is down")})
        
        # Check if it is returning a 200
        if not response.ok:
            errMsg = responseJson["data"].get("message", None)
            raise TypeOfErrorToRaise({"error": True, "errMsg": errMsg})
        
        return responseJson
        
    
    # This makes and handles all requests pertaining to the status of your payment plans
    def _handlePlanStatusRequests(self, type, endpoint, method, data=None):

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
    
        # Checks if it can be parsed to json
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "errMsg": response.text })

        # Checks if it returns a 2xx code
        if response.ok:
            return {"error": False, "returnedData": responseJson}
        else:
            raise PlanStatusError(type, {"error": True, "returnedData": str(responseJson) })

    #gets all subscriptions connected to a merchant's account
    def all(self):
        endpoint = self._baseUrl + self._endpointMap["subscriptions"]["list"]
        method = 'GET'
        return self._handlePlanStatusRequests("list-all-subscription", endpoint, method, data = None)
    
    # def fetch(self, subscription_id=None, subscription_email=None):
    #     if subscription_id:
    #         endpoint = self._baseUrl + self._endpointMap["subscriptions"]["fetch"] + "?seckey="+self._getSecretKey() + "&id="+str(subscription_id)
    #     elif subscription_email:
    #         endpoint = self._baseUrl + self._endpointMap["subscriptions"]["fetch"] + "?seckey="+self._getSecretKey() + "&1="+subscription_email
    #     else:
    #         return "You must pass either plan id or plan name in order to fetch a plan's details"
    #     return self._handlePlanStatusRequests("Fetch", endpoint)
    
    def cancel(self, subscription_id):
        if not subscription_id:
            return "Subscription id was not supplied. Kindly supply one"
        endpoint = self._baseUrl + self._endpointMap["subscriptions"]["cancel"] + "/" + str(subscription_id) + "/cancel"
        method = 'PUT'
        return self._handlePlanStatusRequests("cancel-subscription", endpoint, method, data = None)
    
    # activates a subscription plan
    # Params
    # id: subscription_id *required
    def activate(self, subscription_id):
        if not subscription_id:
            return "Subscription id was not supplied. Kindly supply one"
        endpoint = self._baseUrl + self._endpointMap["subscriptions"]["activate"] + "/" + str(subscription_id) + "/activate"
        method = 'PUT'
        return self._handlePlanStatusRequests("activate-subscription", endpoint, method, data = None)