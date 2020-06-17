from flutterwave_python.rave_exceptions import UssdChargeError, ServerError
from flutterwave_python.rave_payment import Payment
from flutterwave_python.rave_misc import generateTransactionReference
import json

class Ussd(Payment):
    def __init__(self, publicKey, secretKey, encryptionKey,production, usingEnv):
        """ This is the rave object for ussd transactions. It contains the following public functions:\n
        .charge -- This is for making a ussd charge\n
        .verify -- This checks the status of your transaction\n
        """
        super(Ussd, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)
        

    def _handleChargeResponse(self, response, tx_ref, request):
        bankList = {"gtb": "058", "zenith": "057"}
        gtbResponseText = "To complete this transaction, please dial *737*50*charged_amount*159#"
        # This checks if we can parse the json successfully
        
        res =  self._preliminaryResponseChecks(response, UssdChargeError, tx_ref=tx_ref)

        responseJson = res["json"]
        flw_ref = res["flw_ref"]

        # Charge response code of 00 means successful, 02 means failed. Here we check if the code is not 00
        if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
            # If it is we return that further action is required
            # If it is a gtbank account
            if request["accountbank"] == bankList["gtb"]:
                return {"error": False, "validationRequired": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "validationInstruction": gtbResponseText}
            else:
                return {"error": False, "validationRequired": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "validationInstruction": responseJson["data"].get("validateInstructions", None)}

        # If a charge is successful, we return that further action is not required, along with the response
        else:
            return {"error": False, "validationRequired": False, "tx_ref": tx_ref, "flw_ref": flw_ref, "validationInstruction": None}


    # Charge ussd function
    def charge(self, ussdDetails, hasFailed=False):
        """ This is used to charge through ussd.\n
             Parameters are:\n
            ussdDetails (dict) -- This is a dictionary comprising payload parameters.\n
            hasFailed (bool) -- This indicates whether the request had previously failed for timeout handling
        """

        endpoint = self._baseUrl + self._endpointMap["account"]["charge"]

        # Add boilerplate ussd code
        ussdDetails.update({"is_ussd": "1", "payment_type": "ussd"})
        # if transaction reference is not present, generate
        if not ("tx_ref" in ussdDetails):
            ussdDetails.update({"tx_ref": generateTransactionReference()})
        if not ("orderRef" in ussdDetails):
            ussdDetails.update({"orderRef": generateTransactionReference()})
        # Checking for required ussd components (not checking for payment_type, is_ussd, tx_ref or orderRef again to increase efficiency)
        requiredParameters = ["accountbank", "accountnumber", "amount", "email", "phonenumber", "IP"]

        # Should return request is a less efficient call but it is required here because we need bank code in _handleResponses
        return super(Ussd, self).charge(ussdDetails, requiredParameters, endpoint, shouldReturnRequest=True)




