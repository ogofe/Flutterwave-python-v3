from flutterwave_python.rave_exceptions import RaveError, IncompletePaymentDetailsError, CardChargeError, TransactionVerificationError, ServerError
from flutterwave_python.rave_payment import Payment
from flutterwave_python.rave_misc import generateTransactionReference

class Card(Payment):
    """ This is the rave object for card transactions. It contains the following public functions:\n
        .charge -- This is for making a card charge\n
        .validate -- This is called if further action is required i.e. OTP validation\n
        .verify -- This checks the status of your transaction\n
    """
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        super(Card, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)


    # returns true if further action is required, false if it isn't    
    def _handleChargeResponse(self, response, tx_ref, request=None):
        """ This handles charge responses """
        res =  self._preliminaryResponseChecks(response, CardChargeError, tx_ref=tx_ref)

        responseJson = res["json"]
        flw_ref = res["flw_ref"]

        # Checking if there is auth url
        if responseJson["data"].get("authurl", "N/A") == "N/A":
            authUrl = None
        else:
            authUrl = responseJson["data"]["authurl"]

        # If all preliminary checks passed
        if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
            # Otherwise we return that further action is required, along with the response
            suggestedAuth = responseJson["data"].get("suggested_auth", None)
            return {"error": False,  "validationRequired": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "suggestedAuth": suggestedAuth, "authUrl": authUrl}
        else:
            return {"error": False, "status": responseJson["status"],  "validationRequired": False, "tx_ref": tx_ref, "flw_ref": flw_ref, "suggestedAuth": None, "authUrl": authUrl}

    
    def _handleRefundorVoidResponse(self, response, tx_ref, request=None):
        """ This handles charge responses """
        res =  self._preliminaryResponseChecks(response, CardChargeError, tx_ref=tx_ref)

        responseJson = res["json"]
        flw_ref = responseJson["data"]["data"]["authorizeId"]

        # If all preliminary checks passed
        if not (responseJson["data"]["data"].get("responsecode", None) == "RR"):
            # Refund or Void could not be completed
            return {"error": True, "status": responseJson["status"], "message": responseJson["message"], "flw_ref": flw_ref}
        else:
            return {"error": False, "status": responseJson["status"], "message": responseJson["message"], "flw_ref": flw_ref}

    

    # This can be altered by implementing classes but this is the default behaviour
    # Returns True and the data if successful
    def _handleVerifyResponse(self, response, tx_ref):
        """ This handles all responses from the verify call.\n
             Parameters include:\n
            response (dict) -- This is the response Http object returned from the verify call
         """

        # Checking if there was a server error during the call (in this case html is returned instead of json)
        res =  self._preliminaryResponseChecks(response, TransactionVerificationError, tx_ref=tx_ref)
        responseJson = res["json"]

        flw_ref = responseJson["data"]["flw_ref"]
        amount = responseJson["data"]["amount"]
        chargedamount = responseJson["data"]["chargedamount"]
        cardToken = responseJson["data"]["card"]["card_tokens"][0]["embedtoken"]
        vbvmessage = responseJson["data"]["vbvmessage"]
        chargemessage = responseJson["data"]["chargemessage"]
        chargecode = responseJson["data"]["chargecode"]
        currency = responseJson["data"]["currency"]
 
        # Check if the call returned something other than a 200
        if not response.ok:
            errMsg = responseJson["data"].get("message", "Your call failed with no response")
            raise TransactionVerificationError({"error": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "errMsg": errMsg})
        
        # if the chargecode is not 00
        elif not (responseJson["data"].get("chargecode", None) == "00"):
            return {"error": False, "transactionComplete": False, "tx_ref": tx_ref, "flw_ref":flw_ref, "amount": amount, "chargedamount": chargedamount, "cardToken": cardToken, "vbvmessage": vbvmessage, "chargemessage": chargemessage, "chargecode": chargecode, "currency": currency}
        
        else:
            return {"error":False, "transactionComplete": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "amount": amount, "chargedamount": chargedamount, "cardToken": cardToken, "vbvmessage": vbvmessage, "chargemessage": chargemessage, "chargecode": chargecode, "currency": currency}

    
    # Charge card function
    def charge(self, cardDetails, hasFailed=False, chargeWithToken=False):
        """ This is called to initiate the charge process.\n
             Parameters include:\n
            cardDetails (dict) -- This is a dictionary comprising payload parameters.\n
            hasFailed (bool) -- This indicates whether the request had previously failed for timeout handling
        """
        # setting the endpoint
        if not chargeWithToken:
            endpoint = self._baseUrl + self._endpointMap["card"]["charge"] + "?type=" + cardDetails["type"]
            requiredParameters = ["card_number", "cvv", "expiry_month", "expiry_year", "amount", "email", "currency", "tx_ref"]
            # optionalParameters = ["phonenumber", "firstname", "lastname"]
        else: 
            if "charge_type" in cardDetails and cardDetails["charge_type"] == 'preauth':
                endpoint = self._baseUrl + self._endpointMap["preauth"]["charge"]
            else: 
                endpoint = self._baseUrl + self._endpointMap["card"]["chargeSavedCard"]

            requiredParameters = ["currency", "token", "country", "amount", "email", "tx_ref", "IP"]
            # optionalParameters = ["firstname", "lastname"]
            # add token to requiredParameters
            # requiredParameters.append("token")

        if not ("tx_ref" in cardDetails):
            cardDetails.update({"tx_ref":generateTransactionReference()})

        
        return super(Card, self).charge(cardDetails, requiredParameters, endpoint)
    

    def validate(self, details):
        endpoint = self._baseUrl + self._endpointMap["card"]["validate"] + "/" + details["flw_ref"] + "/validate"
        return super(Card, self).validate(details, endpoint)

    def verify(self, details):
        endpoint = self._baseUrl + self._endpointMap["card"]["verify"] + "/" + details["tx_ref"] + "/verify"
        return super(Card, self).verify(details, endpoint)

    def refund(self, details):
        # endpoint = self._baseUrl + self._endpointMap["refund"] +  "/" + details["flw_ref"] + "/refund"
        return super(Card, self).refund(details)



        


