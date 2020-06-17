import os, hashlib, warnings, requests, json
from flutterwave_python.rave_exceptions import ServerError, RefundError
import base64
from Crypto.Cipher import DES3
class RaveBase(object):
    """ This is the core of the implementation. It contains the encryption and initialization functions. It also contains all direct rave functions that require publicKey or secretKey (refund) """
    def __init__(self, publicKey=None, secretKey=None, encryptionKey=None, production=False, usingEnv=True):

        # config variables (protected)
        self._baseUrlMap = ["https://ravesandboxapi.flutterwave.com/", "https://rave-api-v2.herokuapp.com/"]
        self._endpointMap = {
            "beneficiaries":{
                "create": "v3/beneficiaries",
                "list": "v3/beneficiaries",
                "fetch": "v3/beneficiaries",
                "delete": "v3/beneficiaries",
            },
            "banks": {
                "list_bank": "v3/banks",
                "list_branches": "v3/banks",
            },
            "bills": {
                "create":"v3/bills",
                "bulk": "v3/bulk-bills",
                "get-status": "v3/bills",
                "update": "v3/product-orders",
                "bill-category": "v3/bill-categories",
                "bill-service": "v3/bill-items",
                "all": "v3/billers",
            },
            "card": {
                "charge": "v3/charges",
                "validate": "v3/charges/validate-charge",
                "verify": "v3/transactions",
                # "chargeSavedCard": "flwv3-pug/getpaidx/api/tokenized/charge",
            },
            "ebills": {
                "create": "v3/ebills",
                "update": "v3/ebills",
            },
            "preauth": {
                "charge": "flwv3-pug/getpaidx/api/tokenized/preauth_charge",
                "capture": "flwv3-pug/getpaidx/api/capture",
                "refundorvoid": "flwv3-pug/getpaidx/api/refundorvoid"
            },
            "account": {
                "charge": "v3/charges",
                "validate": "v3/charges",
                "verify": "v3/transactions"
            },
            "otp": {
                "create": "v3/otps",
                "validate": "v3/otps",
            },
            "payment_plan": {
                "create": "v3/payment-plans",
                "fetch": "v3/payment-plans",
                "list": "v3/payment-plans",
                "cancel": "v3/payment-plans",
                "edit" :  "v3/payment-plans"
            },
            "subscriptions": {
                "fetch": "v3/subscriptions",
                "list": "v3/subscriptions",
                "cancel": "v3/subscriptions",
                "activate" : "v3/subscriptions"
            },
            "settlements": {
                "list": "v3/settlements",
                "fetch": "v3/settlements",
            },
            "subaccount": {
                "create": "v3/subaccounts",
                "list": "v3/subaccounts",
                "fetch": "v3/subaccounts",
                "update": "v3/subaccounts",
                "delete": "v3/subaccounts",
            },
            "transaction": {
                "all": "v3/transactions",
                "resend_webhook": "v3/transactions",
                "timeline": "v3/transactions",
                "fee": "v3/transactions/fee"
            },
            "transfer": {
                "initiate": "v3/transfers",
                "bulk": "v3/bulk-transfers",
                "fetch": "v3/transfers",
                "fee": "v3/transfers/fee",
                "balance": "v3/balances",
                "account_resolve": "v3/accounts/resolve",
                "bvn": "v3/kyc/bvns"
            },
            "tokens": {
                "charge": "v3/tokenized-charges",
                "update": "v3/tokens",
                "bulk": "v3/bulk-tokenized-charges",
                "get-bulk": "v3/bulk-tokenized-charges",
                "get-bulk-status": "v3/bulk-tokenized-charges",
            },
            "virtual_card": {
                "create": "v3/virtual-cards",
                "list": "v3/virtual-cards",
                "get": "v3/virtual-cards",
                "terminate": "v3/virtual-cards",
                "fund": "v3/virtual-cards",
                "transactions": "v3/virtual-cards",
                "withdraw": "v3/virtual-cards",
                "freeze": "v3/virtual-cards",
                "unfreeze": "v3/virtual-cards",
            },
            "virtual_account":{
                "create" : "v3/virtual-account-numbers",
                "bulk_account": "v3/bulk-virtual-account-numbers",
                "get_bulk_account": "v3/bulk-virtual-account-numbers",
                "get": "v3/virtual-account-numbers",
            },
            "verify": "v3/transactions",
            "refund": "v3/transactions/refunds"
            
        }
        

        # Setting up public and private keys (private)
        # 
        # If we are using environment variables to store secretKey
        if(usingEnv):  
            self.__publicKey = publicKey
            self.__secretKey = os.getenv("RAVE_SECRET_KEY", None)
            self.__encryptionKey = os.getenv("RAVE_ENCRYPTION_KEY", None)

            if (not self.__publicKey) or (not self.__secretKey) or (not self.__encryptionKey):
                raise ValueError("Please set your RAVE_SECRET_KEY and RAVE_ENCRYPTION_KEY environment variable. Otherwise, pass publicKey, secretKey and encryptionKey as arguments and set usingEnv to false")

        # If we are not using environment variables
        else:
            if (not publicKey) or (not secretKey):
                raise ValueError("\n Please provide as arguments your publicKey, secretKey and encryptionKey. \n It is advised however that you provide secret key and encryption key as an environment variables. \n To do this, remove the usingEnv flag and save your keys as environment variables, RAVE_PUBLIC_KEY, RAVE_SECRET_KEY and RAVE_ENCRYPTION_KEY")
    
            else:
                self.__publicKey = publicKey
                self.__secretKey = secretKey
                self.__encryptionKey = encryptionKey

                # Raise warning about not using environment variables
                warnings.warn("Though you can use the usingEnv flag to pass secretKey and encryptionKey as arguments, it is advised to store them in an environment variable, especially in production.", SyntaxWarning)

        # Setting instance variables
        # 
        # production/non-production variables (protected)
        self._isProduction = production 
        self._baseUrl = self._baseUrlMap[production]

        # encryption key (protected)
        # self._encryptionKey = self.__getEncryptionKey()

    

    # This generates the encryption key (private)
    def __getEncryptionKey(self):
        return self.__encryptionKey
        
        # if(self.__secretKey):
        #     hashedseckey = hashlib.md5(self.__secretKey.encode("utf-8")).hexdigest()
        #     hashedseckeylast12 = hashedseckey[-12:]
        #     seckeyadjusted = self.__secretKey.replace('FLWSECK-', '')
        #     seckeyadjustedfirst12 = seckeyadjusted[:12]
        #     key = seckeyadjustedfirst12 + hashedseckeylast12
        #     return key
        # raise ValueError("Please initialize RavePay")
    
    # This returns the public key
    def _getPublicKey(self):
        return self.__publicKey
    
    # This returns the secret key
    def _getSecretKey(self):
        return self.__secretKey

    # This encrypts text
    def _encrypt(self, plainText):
        """ This is the encryption function.\n
             Parameters include:\n 
            plainText (string) -- This is the text you wish to encrypt
        """
        blockSize = 8
        padDiff = blockSize - (len(plainText) % blockSize)
        key = self.__getEncryptionKey()
        cipher = DES3.new(key, DES3.MODE_ECB)
        plainText = "{}{}".format(plainText, "".join(chr(padDiff) * padDiff))
        # cipher.encrypt - the C function that powers this doesn't accept plain string, rather it accepts byte strings, hence the need for the conversion below
        test = plainText.encode('utf-8')
        encrypted = base64.b64encode(cipher.encrypt(test)).decode("utf-8")
        return encrypted
        





    