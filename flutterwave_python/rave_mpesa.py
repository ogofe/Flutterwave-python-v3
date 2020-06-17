from flutterwave_python.rave_exceptions import RaveError, IncompletePaymentDetailsError, AccountChargeError, TransactionVerificationError, TransactionValidationError, ServerError

from flutterwave_python.rave_payment import Payment
from flutterwave_python.rave_misc import generateTransactionReference
import json

class Mpesa(Payment):
    
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        super(Mpesa, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)

    # Charge mobile money function
    def charge(self, accountDetails, hasFailed=False):
        """ This is the mpesa charge call.\n
             Parameters include:\n
            accountDetails (dict) -- These are the parameters passed to the function for processing\n
            hasFailed (boolean) -- This is a flag to determine if the attempt had previously failed due to a timeout\n
        """
        # Setting the endpoint
        endpoint = self._baseUrl + self._endpointMap["account"]["charge"] + "?type=" + accountDetails["type"]
        
        # Adding boilerplate mpesa requirements
        accountDetails.update({"payment_type": "mpesa", "country":"KE", "currency":"KES"})
        
        # If transaction reference is not set 
        if not ("tx_ref" in accountDetails):
            accountDetails.update({"tx_ref": generateTransactionReference()})
        
        # If order reference is not set
        # if not ("orderRef" in accountDetails):
        #     accountDetails.update({"orderRef": generateTransactionReference()})

        # Checking for required account components
        requiredParameters = ["amount", "email", "phone_number", "currency", "tx_ref"]
        res = super(Mpesa, self).charge(accountDetails, requiredParameters, endpoint, isMpesa=True)
        return res

    def validate(self, details):
        endpoint = self._baseUrl + self._endpointMap['account']['validate'] + "/" + details["flw_ref"] + "/validate"
        return super(Mpesa, self).validate(details, endpoint)

    def verify(self, details):
        endpoint = self._baseUrl + self._endpointMap['account']['verify'] + "/" + details["tx_ref"] + "/verify"
        return super(Mpesa, self).verify(details, endpoint)

    def refund(self, details):
        # endpoint = self._baseUrl + self._endpointMap["refund"] +  "/" + details["flw_ref"] + "/refund"
        return super(Mpesa, self).refund(details)