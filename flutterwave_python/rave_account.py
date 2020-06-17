from flutterwave_python.rave_exceptions import AccountChargeError
from flutterwave_python.rave_misc import generateTransactionReference
from flutterwave_python.rave_payment import Payment


class Account(Payment):
    """ This is the rave object for account transactions. It contains the following public functions:\n
        .charge -- This is for making an account charge\n
        .validate -- This is called if further action is required i.e. OTP validation\n
        .verify -- This checks the status of your transaction\n
    """

    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        super(Account, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)


    def _handleChargeResponse(self, response, tx_ref, request=None):
        """ This handles account charge responses """
        # This checks if we can parse the json successfully
        res =  self._preliminaryResponseChecks(response, AccountChargeError, tx_ref=tx_ref)

        response_json = res['json']
        # change - added data before flw_ref
        response_data = response_json['data']
        flw_ref = response_data['flw_ref']

        # If all preliminary checks are passed
        data = {
            'error': False,
            'validationRequired': True,
            'tx_ref': tx_ref,
            'flw_ref': flw_ref,
            'authUrl': None,
            'body': response_data
        }
        if response_data.get("chargeResponseCode") != "00":
            # If contains authurl
            data['authUrl'] = response_data.get("authurl")  # None by default
        else:
            data['validateInstructions'] = response_data['validateInstructions']
        return data

    # Charge account function
    def charge(self, accountDetails, hasFailed=False):
        """ This is the Account charge call.\n
             Parameters include:\n
            accountDetails (dict) -- These are the parameters passed to the function for processing\n
            hasFailed (boolean) -- This is a flag to determine if the attempt had previously failed due to a timeout\n
        """

        # setting the endpoint
        endpoint = self._baseUrl + self._endpointMap['account']['charge'] + "?type=" + accountDetails["type"]

        # It is faster to just update rather than check if it is already present
        # accountDetails.update({'payment_type': 'account'})

        # Generate transaction reference if tx_ref doesn't exist
        accountDetails.setdefault('tx_ref', generateTransactionReference())

        # Checking for required account components
        if accountDetails["type"] != "ach_payment":
            requiredParameters = ['account_bank', 'account_number', 'amount', 'email', 'tx_ref']
        else:
            requiredParameters = ['amount', 'email', 'currency','tx_ref']

        return super(Account, self).charge(accountDetails, requiredParameters, endpoint)

    def validate(self, details):
        endpoint = self._baseUrl + self._endpointMap['account']['validate'] + "/" + details["flw_ref"] + "/validate"
        return super(Account, self).validate(details, endpoint)

    def verify(self, details):
        endpoint = self._baseUrl + self._endpointMap['account']['verify'] + "/" + details["tx_ref"] + "/verify"
        return super(Account, self).verify(details, endpoint)

    def refund(self, details):
        # endpoint = self._baseUrl + self._endpointMap["refund"] +  "/" + details["flw_ref"] + "/refund"
        return super(Account, self).refund(details)