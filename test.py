import os
import asyncio
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io, llm
from livekit.plugins import google, noise_cancellation
import aiohttp
import json
from typing import Optional, Dict, Any
from datetime import datetime

load_dotenv()

# Configuration
class Config:
    # API Endpoints
    SERVICENOW_URL = os.getenv("SERVICENOW_URL")
    SERVICENOW_USER = os.getenv("SERVICENOW_USER")
    SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD")
    
    DUO_API_HOST = os.getenv("DUO_API_HOST")
    DUO_IKEY = os.getenv("DUO_IKEY")
    DUO_SKEY = os.getenv("DUO_SKEY")
    
    SAILPOINT_URL = os.getenv("SAILPOINT_URL")
    SAILPOINT_CLIENT_ID = os.getenv("SAILPOINT_CLIENT_ID")
    SAILPOINT_CLIENT_SECRET = os.getenv("SAILPOINT_CLIENT_SECRET")
    
    MANAGEENGINE_URL = os.getenv("MANAGEENGINE_URL")
    MANAGEENGINE_API_KEY = os.getenv("MANAGEENGINE_API_KEY")
    MANAGEENGINE_TECHNICIAN_KEY = os.getenv("MANAGEENGINE_TECHNICIAN_KEY")


# Integration Clients
class ServiceNowClient:
    """ServiceNow Integration for User Identification"""
    
    def __init__(self):
        self.base_url = Config.SERVICENOW_URL
        self.auth = aiohttp.BasicAuth(
            Config.SERVICENOW_USER, 
            Config.SERVICENOW_PASSWORD
        )
    
    async def get_user_by_employee_id(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user details from ServiceNow"""
        url = f"{self.base_url}/api/now/table/sys_user"
        params = {
            "sysparm_query": f"employee_number={employee_id}",
            "sysparm_fields": "sys_id,name,email,phone,user_name"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=self.auth, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("result"):
                        return data["result"][0]
        return None


class DuoClient:
    """Duo Security Integration for MFA"""
    
    def __init__(self):
        self.api_host = Config.DUO_API_HOST
        self.ikey = Config.DUO_IKEY
        self.skey = Config.DUO_SKEY
    
    async def check_duo_enrollment(self, username: str) -> bool:
        """Check if user has Duo Mobile enrolled"""
        import duo_client
        
        admin_api = duo_client.Admin(
            ikey=self.ikey,
            skey=self.skey,
            host=self.api_host
        )
        
        try:
            users = await asyncio.to_thread(admin_api.get_users_by_name, username)
            if users:
                user = users[0]
                phones = user.get('phones', [])
                for phone in phones:
                    if 'Duo Mobile' in phone.get('capabilities', []):
                        return True
        except Exception as e:
            print(f"Duo enrollment check error: {e}")
        
        return False
    
    async def send_duo_push(self, username: str) -> bool:
        """Send Duo Push notification"""
        import duo_client
        
        auth_api = duo_client.Auth(
            ikey=self.ikey,
            skey=self.skey,
            host=self.api_host
        )
        
        try:
            response = await asyncio.to_thread(
                auth_api.auth,
                'push',
                username=username,
                device='auto',
                type='Password Reset Request',
                pushinfo='action=reset_password'
            )
            return response.get('result') == 'allow'
        except Exception as e:
            print(f"Duo push error: {e}")
            return False
    
    async def send_activation_link(self, phone_number: str) -> bool:
        """Send Duo activation link via SMS"""
        import duo_client
        
        admin_api = duo_client.Admin(
            ikey=self.ikey,
            skey=self.skey,
            host=self.api_host
        )
        
        try:
            # Create enrollment and send SMS
            response = await asyncio.to_thread(
                admin_api.enroll,
                username=phone_number,
                valid_secs=3600
            )
            activation_url = response.get('activation_url')
            # SMS sending logic here
            return True
        except Exception as e:
            print(f"Duo activation error: {e}")
            return False


class SailPointClient:
    """SailPoint Integration for Phone Number Verification"""
    
    def __init__(self):
        self.base_url = Config.SAILPOINT_URL
        self.client_id = Config.SAILPOINT_CLIENT_ID
        self.client_secret = Config.SAILPOINT_CLIENT_SECRET
        self.access_token = None
    
    async def authenticate(self):
        """Get OAuth token"""
        url = f"{self.base_url}/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result.get("access_token")
    
    async def check_phone_registered(self, username: str, phone_number: str) -> bool:
        """Check if phone number is registered for user"""
        if not self.access_token:
            await self.authenticate()
        
        url = f"{self.base_url}/v3/public-identities"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        params = {"filters": f'name eq "{username}"'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        user_phone = data[0].get("attributes", {}).get("phone")
                        return user_phone == phone_number
        
        return False


class ManageEngineClient:
    """ManageEngine SSPR Integration for Password Reset"""
    
    def __init__(self):
        self.base_url = Config.MANAGEENGINE_URL
        self.api_key = Config.MANAGEENGINE_API_KEY
        self.technician_key = Config.MANAGEENGINE_TECHNICIAN_KEY
    
    async def reset_password(self, username: str) -> Optional[str]:
        """Reset user password via ManageEngine SSPR"""
        url = f"{self.base_url}/api/v1/reset_password"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "user_name": username,
            "reset_method": "auto_generate",
            "notify_user": False  # We'll handle notification via voice
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("new_password")
        
        return None
    
    async def create_incident_ticket(self, employee_id: str, username: str, reason: str) -> str:
        """Create incident ticket for manager escalation"""
        url = f"{self.base_url}/api/v1/requests"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "technician_key": self.technician_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "request": {
                "subject": f"Password Reset Request - Employee {employee_id}",
                "description": f"User {username} requires password reset. Reason: {reason}",
                "requester": username,
                "status": "Open",
                "priority": "High",
                "category": "Password Reset"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    return data.get("request", {}).get("id", "N/A")
        
        return "N/A"


# Conversation State Manager
class ConversationState:
    def __init__(self):
        self.employee_id: Optional[str] = None
        self.user_data: Optional[Dict] = None
        self.phone_number: Optional[str] = None
        self.duo_enrolled: bool = False
        self.duo_approved: bool = False
        self.phone_registered: bool = False
        self.new_password: Optional[str] = None
        self.current_step: str = "greeting"


# Custom Agent with Password Reset Logic
class PasswordResetAssistant(Agent):
    def __init__(self) -> None:
        instructions = """You are a helpful password reset voice assistant. 
        Your role is to guide users through the password reset process.
        
        Follow these steps:
        1. Greet the user warmly
        2. Ask for their Employee ID
        3. Guide them through authentication
        4. Help with password reset
        
        Be professional, clear, and patient. Speak naturally."""
        
        super().__init__(instructions=instructions)
        
        # Initialize clients
        self.servicenow = ServiceNowClient()
        self.duo = DuoClient()
        self.sailpoint = SailPointClient()
        self.manageengine = ManageEngineClient()
        
        # Conversation state
        self.state = ConversationState()
    
    async def on_conversation_start(self):
        """Initial greeting"""
        return "Hello! I'm your password reset assistant. To get started, please provide your Employee ID."
    
    async def process_employee_id(self, employee_id: str) -> str:
        """Step 1: Identify user via Employee ID"""
        self.state.employee_id = employee_id
        
        # Query ServiceNow
        user_data = await self.servicenow.get_user_by_employee_id(employee_id)
        
        if not user_data:
            return f"I couldn't find an employee with ID {employee_id}. Please verify and try again."
        
        self.state.user_data = user_data
        self.state.current_step = "authentication"
        
        username = user_data.get("user_name")
        
        # Check Duo enrollment
        self.state.duo_enrolled = await self.duo.check_duo_enrollment(username)
        
        if self.state.duo_enrolled:
            return f"Thank you. I've found your account. I'm sending a Duo push notification to your mobile device. Please approve it to continue."
        else:
            return f"Thank you. I found your account, but you don't have Duo Mobile enrolled. Please provide your registered phone number so I can send you an activation link."
    
    async def handle_duo_authentication(self) -> str:
        """Step 2: Authenticate via Duo"""
        username = self.state.user_data.get("user_name")
        
        if self.state.duo_enrolled:
            # Send Duo push
            approved = await self.duo.send_duo_push(username)
            
            if approved:
                self.state.duo_approved = True
                self.state.current_step = "password_reset"
                return "Authentication successful! I'll now reset your password."
            else:
                return "The Duo push was not approved. Please try again or contact your manager for assistance."
        else:
            return "Please provide your registered phone number."
    
    async def handle_phone_number(self, phone_number: str) -> str:
        """Handle phone number for Duo activation or verification"""
        self.state.phone_number = phone_number
        username = self.state.user_data.get("user_name")
        
        # Check if phone is registered via SailPoint
        self.state.phone_registered = await self.sailpoint.check_phone_registered(
            username, phone_number
        )
        
        if not self.state.phone_registered:
            # Escalate to manager
            ticket_id = await self.manageengine.create_incident_ticket(
                self.state.employee_id,
                username,
                "Phone number not registered in system"
            )
            return f"I'm sorry, but the phone number you provided is not registered in our system. I've created a ticket (ID: {ticket_id}) and your manager will contact you shortly to help with the password reset."
        
        # Send activation link
        await self.duo.send_activation_link(phone_number)
        return f"I've sent an activation link to {phone_number}. Please install the Duo Mobile app and complete the setup. Once done, call back to reset your password."
    
    async def reset_user_password(self) -> str:
        """Step 3: Reset password via ManageEngine"""
        username = self.state.user_data.get("user_name")
        
        new_password = await self.manageengine.reset_password(username)
        
        if new_password:
            self.state.new_password = new_password
            self.state.current_step = "complete"
            
            # Format password for voice readability
            password_spoken = self.format_password_for_speech(new_password)
            
            return f"Your password has been successfully reset. Your new temporary password is: {password_spoken}. Please write this down. You'll be required to change it on your next login. Is there anything else I can help you with?"
        else:
            return "I encountered an error while resetting your password. Please contact your IT support team."
    
    def format_password_for_speech(self, password: str) -> str:
        """Format password for clear voice communication"""
        # Add pauses and spell out special characters
        formatted = ""
        char_map = {
            "!": "exclamation mark",
            "@": "at sign",
            "#": "hash",
            "$": "dollar sign",
            "%": "percent",
            "^": "caret",
            "&": "ampersand",
            "*": "asterisk",
            "(": "open parenthesis",
            ")": "close parenthesis",
            "-": "dash",
            "_": "underscore",
            "=": "equals",
            "+": "plus"
        }
        
        for char in password:
            if char.isalpha():
                formatted += f"{char.upper()} "
            elif char.isdigit():
                formatted += f"{char} "
            elif char in char_map:
                formatted += f"{char_map[char]} "
            else:
                formatted += f"{char} "
        
        return formatted.strip()


# Function calling for the LLM
async def setup_function_calling(session: AgentSession, assistant: PasswordResetAssistant):
    """Setup function calling for workflow management"""
    
    @session.llm.function()
    async def verify_employee_id(employee_id: str) -> str:
        """Verify employee ID and retrieve user information"""
        return await assistant.process_employee_id(employee_id)
    
    @session.llm.function()
    async def authenticate_duo() -> str:
        """Authenticate user via Duo"""
        return await assistant.handle_duo_authentication()
    
    @session.llm.function()
    async def register_phone_number(phone_number: str) -> str:
        """Register or verify phone number"""
        return await assistant.handle_phone_number(phone_number)
    
    @session.llm.function()
    async def reset_password() -> str:
        """Reset user password"""
        return await assistant.reset_user_password()


# Main Agent Server
server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    # Initialize assistant
    assistant = PasswordResetAssistant()
    
    # Create session with Gemini
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Puck",
            instructions="""You are a password reset voice assistant. Guide users through:
            
            1. Collecting Employee ID - call verify_employee_id()
            2. Duo authentication - call authenticate_duo()
            3. Phone verification if needed - call register_phone_number()
            4. Password reset - call reset_password()
            
            Be conversational and helpful. Extract information from user speech and call appropriate functions."""
        )
    )
    
    # Setup function calling
    await setup_function_calling(session, assistant)
    
    # Start session
    await session.start(
        room=ctx.room,
        agent=assistant,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony()
                if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                else noise_cancellation.BVC(),
            ),
        ),
    )
    
    # Send initial greeting
    initial_message = await assistant.on_conversation_start()
    await session.say(initial_message)


if __name__ == "__main__":
    server.run()
