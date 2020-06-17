from flutterwave_python.rave_account import Account
from flutterwave_python.rave_bills import Bills
from flutterwave_python.rave_banks import Banks
from flutterwave_python.rave_card import Card
from flutterwave_python.rave_ebills import Ebills
from flutterwave_python.rave_francophone import Francophone
from flutterwave_python.rave_ghmobile import GhMobile
from flutterwave_python.rave_mpesa import Mpesa
from flutterwave_python.rave_otp import Otp
from flutterwave_python.rave_paymentplan import PaymentPlan
from flutterwave_python.rave_preauth import Preauth
from flutterwave_python.rave_base import RaveBase
from flutterwave_python.rave_beneficiaries import Beneficiaries
from flutterwave_python.rave_rwmobile import RWMobile
from flutterwave_python.rave_settlement import Settlement
from flutterwave_python.rave_subaccounts import SubAccount
from flutterwave_python.rave_subscription import Subscriptions
from flutterwave_python.rave_tokens import Tokens
from flutterwave_python.rave_transaction import Transaction
from flutterwave_python.rave_transfer import Transfer
from flutterwave_python.rave_ugmobile import UGMobile
from flutterwave_python.rave_ussd import Ussd
from flutterwave_python.rave_virtualaccount import VirtualAccount
from flutterwave_python.rave_virtualcard import VirtualCard
from flutterwave_python.rave_zbmobile import ZBMobile


class Rave:
    
    def __init__(self, publicKey, secretKey, encryptionKey, production=False, usingEnv=True):
        """ This is main organizing object. It contains the following:\n
            rave.Account -- For bank account transactions\n
            rave.Bills -- For Bills payments\n
            rave.Card -- For card transactions\n
            rave.Francophone -- For West African Francophone mobile money transactions\n
            rave.GhMobile -- For Ghana mobile money transactions\n
            rave.Mpesa -- For mpesa transactions\n
            rave.PaymentPlan -- For payment plan creation and operation\n
            rave.Preauth -- For preauthorized transactions\n
            rave.RWMobile -- For Rwanda mobile money transactions\n
            rave.Settlement -- For settled transactions\n
            rave.SubAccount -- For creation of subaccounts for split payment operations\n
            rave.Transfer -- For Payouts and transfers\n
            rave.UGMobile -- For Uganda mobile money transactions\n
            rave.Ussd -- For ussd transactions\n
            rave.VirtualAccount -- For virtual account transactions\n
            rave.VirtualCard -- For virtual card transactions\n 
            rave.ZBMobile -- For Zambia mobile money transactions\n
            
        """

        # classes = (
        #     Account, Banks, Bills, Card, Ebills, Francophone, GhMobile, Mpesa, Otp, PaymentPlan, Preauth, Beneficiaries, RWMobile, Settlement, SubAccount, Subscriptions, Transfer, UGMobile, Ussd, VirtualAccount, VirtualCard, ZBMobile
        # )

        # for _class in classes:
        #     attr = _class(publicKey, secretKey, encryptionKey, production, usingEnv)
        #     setattr(self, _class.__name__ , attr)


        self.Account = Account(publicKey, secretKey, encryptionKey, production, usingEnv)		         
        self.Banks = Banks(publicKey, secretKey, encryptionKey, production, usingEnv)		         
        self.Beneficiaries = Beneficiaries(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.Bills = Bills(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.Card = Card(publicKey, secretKey, encryptionKey, production, usingEnv)
        self.Ebills = Ebills(publicKey, secretKey, encryptionKey, production,  usingEnv)		            
        self.Francophone = Francophone(publicKey, secretKey, encryptionKey, production, usingEnv)		            
        self.GhMobile = GhMobile(publicKey, secretKey, encryptionKey, production, usingEnv)		          
        self.Mpesa = Mpesa(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.Otp = Otp(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.PaymentPlan = PaymentPlan(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.Preauth = Preauth(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.RWMobile = RWMobile(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.Settlement = Settlement(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.SubAccount = SubAccount(publicKey, secretKey, encryptionKey, production, usingEnv)
        self.Subscriptions = Subscriptions(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.Tokens = Tokens(publicKey, secretKey, encryptionKey, production, usingEnv)
        self.Transaction = Transaction(publicKey, secretKey, encryptionKey, production, usingEnv)
        self.Transfer = Transfer(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.UGMobile = UGMobile(publicKey, secretKey, encryptionKey, production, usingEnv)
        self.Ussd = Ussd(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.VirtualAccount = VirtualAccount(publicKey, secretKey, encryptionKey, production, usingEnv)
        self.VirtualCard = VirtualCard(publicKey, secretKey, encryptionKey, production, usingEnv)		
        self.ZBMobile = ZBMobile(publicKey, secretKey, encryptionKey, production, usingEnv)
        
      
