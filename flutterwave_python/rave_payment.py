import requests, json, copy
from flutterwave_python.rave_base import RaveBase
from flutterwave_python.rave_exceptions import RaveError, IncompletePaymentDetailsError, AuthMethodNotSupportedError, TransactionChargeError, TransactionVerificationError, TransactionValidationError, ServerError, RefundError, PreauthCaptureError
from flutterwave_python.rave_misc import checkIfParametersAreComplete

response_object = {
    "error": False,
    "transactionComplete": False,
    "flw_ref": "",
    "tx_ref": "",
    "chargecode": '00',
    "status": "",
    "vbvcode": "",
    "vbvmessage": "",
    "acctmessage": "",
    "currency": "",
    "chargedamount": 00,
    "chargemessage": ""
}

# All payment subclasses are encrypted classes
class Payment(RaveBase):
    """ This is the base class for all the payments """
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        # Instantiating the base class
        super(Payment, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)

    @classmethod
    def retrieve(cls, mapping, *keys): 
        return (mapping[key] for key in keys) 

    @classmethod
    def deleteUnnecessaryKeys(cls,response_dict, *keys):
        for key in keys:
            del response_dict[key]
        return response_dict

    def _preliminaryResponseChecks(self, response, TypeOfErrorToRaise, tx_ref=None, flw_ref=None):
        preliminary_error_response = copy.deepcopy(response_object)
        preliminary_error_response = Payment.deleteUnnecessaryKeys(preliminary_error_response, "transactionComplete", "chargecode", "vbvmessage", "vbvcode", "acctmessage", "currency")

        # Check if we can obtain a json
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "errMsg": response})


        # Check if the response contains data parameter
        if responseJson.get("data", None):
            if tx_ref:
                flw_ref = responseJson["data"].get("flw_ref", None)
            if flw_ref:
                tx_ref = responseJson["data"].get("tx_ref", None)
        else:
            raise TypeOfErrorToRaise({"error": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "errMsg": responseJson.get("message", "Server is down")})
        
        # Check if it is returning a 200
        if not response.ok:
            errMsg = responseJson["data"].get("message", None)
            raise TypeOfErrorToRaise({"error": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "errMsg": errMsg})
        
        return {"json": responseJson, "flw_ref": flw_ref, "tx_ref": tx_ref}

    def _handleChargeResponse(self, response, tx_ref, request=None, isMpesa=False):
        """ This handles transaction charge responses """

        # If we cannot parse the json, it means there is a server error
        res = self._preliminaryResponseChecks(response, TransactionChargeError, tx_ref=tx_ref)
        
        responseJson = res["json"]
        flw_ref = responseJson["data"]["flw_ref"]

        if isMpesa:
            return {"error": False, "status": responseJson["status"], "validationRequired": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "narration": responseJson["data"]["narration"], "data":responseJson["data"]}
        else:
            # if all preliminary tests pass
            if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
                if responseJson["data"].get("currency", 'None') == 'UGX':
                    return {"error": False, "status": responseJson["status"],  "validationRequired": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "message": responseJson["message"], "data":responseJson["data"] }

                return {"error": False, "status": responseJson["status"],"validationRequired": True, "tx_ref": tx_ref, "flw_ref": flw_ref, "message": responseJson["message"], "data":responseJson["data"]}
            else:
                return {"error": True,  "validationRequired": False, "tx_ref": tx_ref, "flw_ref": flw_ref}
    
    def _handleCaptureResponse(self, response, request=None):
        """ This handles transaction charge responses """

        # If we cannot parse the json, it means there is a server error
        res = self._preliminaryResponseChecks(response, PreauthCaptureError, tx_ref='')
        
        responseJson = res["json"]
        flw_ref = responseJson["data"]["flw_ref"]
        tx_ref = responseJson["data"]["tx_ref"]
        
        # if all preliminary tests pass
        if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
            return {"error": False,  "validationRequired": True, "tx_ref": tx_ref, "flw_ref": flw_ref}
        else:
            return {"error": False, "status":responseJson["status"], "message": responseJson["message"],  "validationRequired": False, "tx_ref": tx_ref, "flw_ref": flw_ref}


    # This can be altered by implementing classes but this is the default behaviour
    # Returns True and the data if successful
    def _handleVerifyResponse(self, response, tx_ref):
        """ This handles all responses from the verify call.\n
             Parameters include:\n
            response (dict) -- This is the response Http object returned from the verify call
         """
        verify_response = copy.deepcopy(response_object)
        res = self._preliminaryResponseChecks(response, TransactionVerificationError, tx_ref=tx_ref)


        responseJson = res["json"]
        # retrieve necessary properties from response 
        verify_response["status"] = responseJson['status']
        verify_response['flw_ref'], verify_response["tx_ref"], verify_response["proccessor_response"], verify_response["narration"], verify_response["currency"], verify_response["payment_type"], verify_response["amount"], verify_response["auth_model"] = Payment.retrieve(responseJson['data'], "flw_ref", "tx_ref", "processor_response", "narration", "currency", "payment_type", "amount", "auth_model")

        # Check if the chargecode is 00
        if verify_response['status'] == "success":
            verify_response["error"] = False
            verify_response["transactionComplete"] = True
            return verify_response
        
        else:
            verify_response["error"] = True # changed to True on 15/10/2018
            verify_response["transactionComplete"] = False
            return verify_response
        
        # # Check if the chargecode is 00
        # if not (responseJson["data"].get("chargecode", None) == "00"):
        #     return {"error": False, "transactionComplete": False, "tx_ref": tx_ref, "flw_ref":flw_ref}
        
        # else:
        #     return {"error": False, "transactionComplete": True, "tx_ref": tx_ref, "flw_ref":flw_ref}

    
    # returns true if further action is required, false if it isn't    
    def _handleValidateResponse(self, response, flw_ref, request=None):
        """ This handles validation responses """

        # If json is not parseable, it means there is a problem in server
            
        res = self._preliminaryResponseChecks(response, TransactionValidationError, flw_ref=flw_ref)

        responseJson = res["json"]
        if responseJson["data"].get("tx") == None:
            tx_ref = responseJson["data"]["tx_ref"]
        else:
            tx_ref = responseJson["data"]["tx"]["tx_ref"]

        # Of all preliminary checks passed
        if not (responseJson["data"].get("tx", responseJson["data"]).get("chargeResponseCode", None) == "00"):
            errMsg = responseJson["data"].get("tx", responseJson["data"]).get("message", None)
            raise TransactionValidationError({"error": True, "tx_ref": tx_ref, "flw_ref": flw_ref , "errMsg": errMsg})

        else:
            return {"status": responseJson["status"], "message": responseJson["message"], "error": False, "tx_ref": tx_ref, "flw_ref": flw_ref}


    # Charge function (hasFailed is a flag that indicates there is a timeout), shouldReturnRequest indicates whether to send the request back to the _handleResponses function
    def charge(self, paymentDetails, requiredParameters, endpoint, shouldReturnRequest=False, isMpesa=False):
        """ This is the base charge call. It is usually overridden by implementing classes.\n
             Parameters include:\n
            paymentDetails (dict) -- These are the parameters passed to the function for processing\n
            requiredParameters (list) -- These are the parameters required for the specific call\n
            hasFailed (boolean) -- This is a flag to determine if the attempt had previously failed due to a timeout\n
            shouldReturnRequest -- This determines whether a request is passed to _handleResponses\n
        """
        # Checking for required components
        try:
            checkIfParametersAreComplete(requiredParameters, paymentDetails)
        except: 
            raise
        
        # Performing shallow copy of payment details to prevent tampering with original
        paymentDetails = copy.copy(paymentDetails)
        
        # Adding PBFPubKey param to paymentDetails
        paymentDetails.update({"public_key": self._getPublicKey()})

        # Collating request headers
        headers = {
            'content-type': 'application/json',
            'authorization' : 'Bearer ' + self._getSecretKey(),
        }
        if "token" in paymentDetails:
            paymentDetails.update({"SECKEY": self._getSecretKey()})
            # print(json.dumps(paymentDetails))
            response = requests.post(endpoint, headers=headers, data=json.dumps(paymentDetails))
        elif paymentDetails["type"] != "card":
            response = requests.post(endpoint, headers=headers, data=json.dumps(paymentDetails))
        else:
            # Encrypting payment details (_encrypt is inherited from RaveEncryption)
            encryptedPaymentDetails = self._encrypt(json.dumps(paymentDetails))
            
            # Collating the payload for the request
            payload = {
                "public_key": paymentDetails["public_key"],
                "client": encryptedPaymentDetails
            }
            response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
        
        if shouldReturnRequest:
            if isMpesa:
                return self._handleChargeResponse(response, paymentDetails["tx_ref"], paymentDetails, True)
            return self._handleChargeResponse(response, paymentDetails["tx_ref"], paymentDetails)
        else:
            if isMpesa:
                return self._handleChargeResponse(response, paymentDetails["tx_ref"], paymentDetails, True)
            return self._handleChargeResponse(response, paymentDetails["tx_ref"])
            
       

    def validate(self, payload, endpoint=None):
        """ This is the base validate call.\n
             Parameters include:\n
            flw_ref (string) -- This is the flutterwave reference returned from a successful charge call. You can access this from action["flw_ref"] returned from the charge call\n
            otp (string) -- This is the otp sent to the user \n
        """

        if not endpoint: 
            endpoint = self._baseUrl + self._endpointMap["account"]["validate"]
            
        # Collating request headers
        headers = {
            'content-type': 'application/json',
            'authorization' : 'Bearer ' + self._getSecretKey(),

        }
        
        # payload = {
        #     "otp": otp,
        #     "type": tranx_type,
        #     "public_key": self._getPublicKey(),
        #     # "transactionreference": flw_ref, 
        #     # "transaction_reference": flw_ref,
        # }
        
        response = requests.post(endpoint, headers = headers, data=json.dumps(payload))
        return self._handleValidateResponse(response, payload)
        
    # Verify charge
    def verify(self, details, endpoint=None):
        """ This is used to check the status of a transaction.\n
             Parameters include:\n
            tx_ref (string) -- This is the transaction reference that you passed to your charge call. If you didn't define a reference, you can access the auto-generated one from payload["tx_ref"] or action["tx_ref"] from the charge call\n
        """
        if not endpoint:
            endpoint = self._baseUrl + self._endpointMap["verify"] +  "/" + details["tx_ref"] + "/verify"

        # Collating request headers
        headers = {
            'content-type': 'application/json',
            'authorization' : 'Bearer ' + self._getSecretKey(),
        }

        # # Payload for the request headers
        # payload = {
        #     "tx_ref": tx_ref,
        #     # "SECKEY": self._getSecretKey()
        # }
        response = requests.get(endpoint, headers=headers, data=json.dumps(details))
        return self._handleVerifyResponse(response, details)

    #Refund call
    def refund(self, details):
        """ This is used to refund a transaction from any of Rave's component objects.\n 
             Parameters include:\n
            flw_ref (string) -- This is the flutterwave reference returned from a successful call from any component. You can access this from action["flw_ref"] returned from the charge call
        """
        
        headers = {
            "Content-Type":"application/json",
            'authorization' : 'Bearer ' + self._getSecretKey(),
        }
        endpoint = self._baseUrl + self._endpointMap["refund"]

        response = requests.post(endpoint, headers = headers, data=json.dumps(details))

        try:
            responseJson = response.json()
        except ValueError:
            raise ServerError(response)
        
        if responseJson.get("status", None) == "error":
            raise RefundError(responseJson.get("message", None))
        elif responseJson.get("status", None) == "success":
            return True, responseJson.get("data", None)

        # return self._handleValidateResponse(response, details)


        


