from flutterwave_python.rave_payment import Payment
from flutterwave_python.rave_misc import generateTransactionReference
import json

class GhMobile(Payment):
    
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        super(GhMobile, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)


    # Charge mobile money function
    def charge(self, accountDetails, hasFailed=False):
        """ This is the ghMobile charge call.
             Parameters include:\n
            accountDetails (dict) -- These are the parameters passed to the function for processing\n
            hasFailed (boolean) -- This is a flag to determine if the attempt had previously failed due to a timeout\n
        """

        endpoint = self._baseUrl + self._endpointMap["account"]["charge"] + "?type=" + accountDetails["type"]
        
        # It is faster to add boilerplate than to check if each one is present
        accountDetails.update({"type": "mobile_money_ghana", "currency":"GHS"})
        
        # If transaction reference is not set 
        if not ("tx_ref" in accountDetails):
            accountDetails.update({"tx_ref": generateTransactionReference()})
        
        # If order reference is not set
        if not ("orderRef" in accountDetails):
            accountDetails.update({"orderRef": generateTransactionReference()})

        # Checking for required account components
        requiredParameters = ["amount", "email", "phone_number", "network", "currency", "tx_ref"]
        return super(GhMobile, self).charge(accountDetails, requiredParameters, endpoint)

    
    def validate(self, details):
        endpoint = self._baseUrl + self._endpointMap['account']['validate'] + "/" + details["flw_ref"] + "/validate"
        return super(GhMobile, self).validate(details, endpoint)

    def verify(self, details):
        endpoint = self._baseUrl + self._endpointMap['account']['verify'] + "/" + details["tx_ref"] + "/verify"
        return super(GhMobile, self).verify(details, endpoint)

    def refund(self, details):
        # endpoint = self._baseUrl + self._endpointMap["refund"] +  "/" + details["flw_ref"] + "/refund"
        return super(GhMobile, self).refund(details)

    

