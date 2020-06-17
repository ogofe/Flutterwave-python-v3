from flutterwave_python.rave_exceptions import RaveError, IncompletePaymentDetailsError, MobileChargeError, TransactionVerificationError, TransactionValidationError, ServerError
from flutterwave_python.rave_payment import Payment
from flutterwave_python.rave_misc import generateTransactionReference
import json
import webbrowser

class Francophone(Payment):
    
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        super(Francophone, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)


    # returns true if further action is required, false if it isn't    
    def _handleChargeResponse(self, response, tx_ref, request=None):
        """ This handles charge responses """
        res =  self._preliminaryResponseChecks(response, MobileChargeError, tx_ref=tx_ref)

        responseJson = res["json"]
        flwRef = res["flwRef"]

        # Checking if there is redirect url
        if responseJson["data"]["data"].get("redirect_url", "N/A") == "N/A":
            redirectUrl = None
        else:
            redirectUrl = responseJson["meta"]["authorization"]["redirect_url"]

        # If all preliminary checks passed
        if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
            # Otherwise we return that further action is required, along with the response
            suggestedAuth = responseJson["data"].get("suggested_auth", None)
            return {"error": False,  "validationRequired": True, "tx_ref": tx_ref, "flwRef": flwRef, "suggestedAuth": suggestedAuth, "redirectUrl": redirectUrl}
        else:
            return {"error": False, "status": responseJson["status"],  "validationRequired": False, "tx_ref": tx_ref, "flwRef": flwRef, "suggestedAuth": None, "redirectUrl": redirectUrl}
    
    # Charge mobile money function
    def charge(self, accountDetails, hasFailed=False):
        """ This is the charge call for central francophone countries.
             Parameters include:\n
            accountDetails (dict) -- These are the parameters passed to the function for processing\n
            hasFailed (boolean) -- This is a flag to determine if the attempt had previously failed due to a timeout\n
        """

        endpoint = self._baseUrl + self._endpointMap["account"]["charge"] + "?type=" + accountDetails["type"]
        # It is faster to add boilerplate than to check if each one is present
        accountDetails.update({"type": "mobile_money_franco"})
        
        # If transaction reference is not set 
        if not ("tx_ref" in accountDetails):
            accountDetails.update({"tx_ref": generateTransactionReference()})
        # If order reference is not set
        # if not ("order_Ref" in accountDetails):
        #     accountDetails.update({"orderRef": generateTransactionReference()})
        # Checking for required account components
        requiredParameters = ["amount", "email", "phone_number", "currency", "tx_ref"]
        return super(Francophone, self).charge(accountDetails, requiredParameters, endpoint)

    def validate(self, details):
        endpoint = self._baseUrl + self._endpointMap['account']['validate'] + "/" + details["flw_ref"] + "/validate"
        return super(Francophone, self).validate(details, endpoint)

    def verify(self, details):
        endpoint = self._baseUrl + self._endpointMap['account']['verify'] + "/" + details["tx_ref"] + "/verify"
        return super(Francophone, self).verify(details, endpoint)

    def refund(self, details):
        # endpoint = self._baseUrl + self._endpointMap["refund"] +  "/" + details["flw_ref"] + "/refund"
        return super(Francophone, self).refund(details)
