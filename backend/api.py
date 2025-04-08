from livekit.agents import llm
import enum
from typing import Annotated
import logging
from db_driver import DatabaseDriver

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()

class PolicyDetails(enum.Enum):
    POLICY_NUMBER = "policy_number"
    CUSTOMER_NAME = "customer_name"
    POLICY_TYPE = "policy_type"
    START_DATE = "start_date"
    END_DATE = "end_date"
    STATUS = "status"

class CustomerDetails(enum.Enum):
    CUSTOMER_ID = "customer_id"
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"

class ClaimDetails(enum.Enum):
    CLAIM_ID = "claim_id"
    POLICY_ID = "policy_id"
    STATUS = "status"
    AMOUNT = "amount"
    DESCRIPTION = "description"

class AssistantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()

        self._policy_details = {
            PolicyDetails.POLICY_NUMBER: "",
            PolicyDetails.CUSTOMER_NAME: "",
            PolicyDetails.POLICY_TYPE: "",
            PolicyDetails.START_DATE: "",
            PolicyDetails.END_DATE: "",
            PolicyDetails.STATUS: ""
        }

        self._customer_details = {
            CustomerDetails.CUSTOMER_ID: "",
            CustomerDetails.NAME: "", 
            CustomerDetails.EMAIL: "", 
            CustomerDetails.PHONE: ""
        }

        self._claim_details = {
            ClaimDetails.CLAIM_ID: "",
            ClaimDetails.POLICY_ID: "",
            ClaimDetails.STATUS: "",
            ClaimDetails.AMOUNT: "",
            ClaimDetails.DESCRIPTION: ""
        }

        self.current_policy_id = None
        self.current_customer_id = None
        self.current_customer_name = None

    def get_policy_str(self):
        policy_str = ""
        for key, value in self._policy_details.items():
            policy_str += f"{key.value}: {value}\n"
        return policy_str

    def get_customer_str(self):
        customer_str = ""
        for key, value in self._customer_details.items():
            customer_str += f"{key.value}: {value}\n"
        return customer_str
    
    def get_claim_str(self):
        claim_str = ""
        for key, value in self._claim_details.items():
            claim_str += f"{key.value}: {value}\n"
        return claim_str
    
    @llm.ai_callable(description="Lookup an insurance policy by its policy number")
    def lookup_policy(self, policy_number: Annotated[str, llm.TypeInfo(description="The policy number to lookup")]):
        logger.info("lookup policy - policy_number %s", policy_number)

        result = DB.get_policy_by_number(policy_number)
        if result is None:
            return "Policy not found"
        
        self._policy_details = {
            PolicyDetails.POLICY_NUMBER: policy_number,
            PolicyDetails.CUSTOMER_NAME: result.customer_name,
            PolicyDetails.POLICY_TYPE: result.policy_type,
            PolicyDetails.START_DATE: result.start_date,
            PolicyDetails.END_DATE: result.end_date,
            PolicyDetails.STATUS: result.status
        }

        return f"The policy details are: \n{self.get_policy_str()}"
    
    @llm.ai_callable(description="get the details of the current policy")
    def get_policy_details(self):
        logger.info("get policy details")
        if not self.get_policy_str():
            return "No policy selected yet. Please provide a policy number."
        return f"The policy details are: {self.get_policy_str()}"
    
    @llm.ai_callable(description="create a new insurance policy")
    def create_policy(
        self, 
        policy_number: Annotated[str, llm.TypeInfo(description="The policy number")],
        policy_type: Annotated[str, llm.TypeInfo(description="The type of policy (e.g., General Liability)")],
        start_date: Annotated[str, llm.TypeInfo(description="The policy start date (YYYY-MM-DD)")],
        end_date: Annotated[str, llm.TypeInfo(description="The policy end date (YYYY-MM-DD)")],
        status: Annotated[str, llm.TypeInfo(description="The status of the policy (e.g., Active, Inactive)")],
        premium: Annotated[float, llm.TypeInfo(description="The premium amount for the policy")]
    ):
        logger.info(
            "create policy - policy_number: %s, policy_type: %s, start_date: %s, end_date: %s, status: %s, premium: %s",
            policy_number, policy_type, start_date, end_date, status, premium
        )
        result = DB.create_policy(self.current_customer_id, policy_number, policy_type, start_date, end_date, status, premium)
        if result is None:
            return "Failed to create policy"
        
        self.current_policy_id = result.policy_id
        
        self._policy_details = {
            PolicyDetails.POLICY_NUMBER: policy_number,
            PolicyDetails.CUSTOMER_NAME: result.customer_name,
            PolicyDetails.POLICY_TYPE: policy_type,
            PolicyDetails.START_DATE: start_date,
            PolicyDetails.END_DATE: end_date,
            PolicyDetails.STATUS: status
        }

        return f"Policy created successfully!\n{self.get_policy_str()}"
    
    @llm.ai_callable(description="File a new claim for the current policy")
    def file_claim(
        self,
        amount: Annotated[float, llm.TypeInfo(description="The amount of the claim")],
        description: Annotated[str, llm.TypeInfo(description="The description of the claim")]
    ):
        logger.info("file claim - amount: %s, description: %s", amount, description)

        if not self.has_policy():
            return "Please provide your policy number first before filing a claim."

        Claim = DB.create_claim(
            policy_id=self.current_policy_id,
            amount=amount,
            description=description
        )

        self._claim_details = {
            ClaimDetails.CLAIM_ID: Claim.claim_id,
            ClaimDetails.POLICY_ID: self.current_policy_id,
            ClaimDetails.STATUS: Claim.status,
            ClaimDetails.AMOUNT: Claim.amount,
            ClaimDetails.DESCRIPTION: Claim.description
        }

        return f"I've filed a new claim for you. Claim Details: \n{self.get_claim_str()}"
    
    @llm.ai_callable(description="Lookup a claim status by claim number")
    def lookup_claim_status(
        self,
        claim_id: Annotated[int, llm.TypeInfo(description="The claim number to check")]
    ):
        logger.info("lookup claim status - claim_id: %s", claim_id)

        claim_status = DB.get_claim_status(claim_id)
        if claim_status:
            return f"The claim status is: {claim_status}"
        else:
            return f"I couldn't find a claim with number {claim_id}."
        
    @llm.ai_callable(description="Register or retrieve a customer profile")
    def create_or_lookup_customer(
        self,
        customer_name: Annotated[str, llm.TypeInfo(description="The full name of the customer")],
        customer_email: Annotated[str, llm.TypeInfo(description="The email of the customer")],
        customer_phone: Annotated[str, llm.TypeInfo(description="The phone number of the customer")]
    ):
        logger.info("create_or_lookup_customer - name: %s, email: %s, phone: %s", customer_name, customer_email, customer_phone)

        Customer = DB.create_customer(
            name=customer_name,
            email=customer_email,
            phone=customer_phone
        )

        self._customer_details = {
            CustomerDetails.CUSTOMER_ID: Customer.customer_id,
            CustomerDetails.NAME: customer_name, 
            CustomerDetails.EMAIL: customer_email, 
            CustomerDetails.PHONE: customer_phone
        }

        self.current_customer_id = Customer.customer_id
        self.current_customer_name = customer_name

        return f"Customer profile ready! Customer profile details: \n{self.get_customer_str()}."
    
    def has_policy(self):
        return self.current_policy_id is not None
    
    def has_customer(self):
        return self.current_customer_id is not None
    


