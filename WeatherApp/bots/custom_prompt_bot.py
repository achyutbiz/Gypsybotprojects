
from datetime import datetime
import re
from recognizers_number import recognize_number, Culture
from recognizers_date_time import recognize_datetime

from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    TurnContext,
    UserState,
    MessageFactory,
)

from data_models import ConversationFlow, Question, UserProfile


class ValidationResult:
    def __init__(
        self, is_valid: bool = False, value: object = None, message: str = None
    ):
        self.is_valid = is_valid
        self.value = value
        self.message = message


class CustomPromptBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        if conversation_state is None:
            raise TypeError(
                "[CustomPromptBot]: Missing parameter. conversation_state is required but None was given"
            )
        if user_state is None:
            raise TypeError(
                "[CustomPromptBot]: Missing parameter. user_state is required but None was given"
            )

        self.conversation_state = conversation_state
        self.user_state = user_state

        self.flow_accessor = self.conversation_state.create_property("ConversationFlow")
        self.profile_accessor = self.user_state.create_property("UserProfile")



    async def on_message_activity(self, turn_context: TurnContext):
        # Get the state properties from the turn context.
        profile = await self.profile_accessor.get(turn_context, UserProfile)
        flow = await self.flow_accessor.get(turn_context, ConversationFlow)

        await self._fill_out_user_profile(flow, profile, turn_context)

        # Save changes to UserState and ConversationState
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def _fill_out_user_profile(
        self, flow: ConversationFlow, profile: UserProfile, turn_context: TurnContext
    ):
        user_input = turn_context.activity.text.strip()

        # ask for name
        if flow.last_question_asked == Question.NONE:
            await turn_context.send_activity(
                MessageFactory.text("Let's get started. What is your name?")
            )
            flow.last_question_asked = Question.NAME

        # validate name then ask for email
        elif flow.last_question_asked == Question.NAME:
            validate_result = self._validate_name(user_input)
            if not validate_result.is_valid:
                await turn_context.send_activity(
                    MessageFactory.text(validate_result.message)
                )
            
            else:
                profile.name = validate_result.value
                await turn_context.send_activity(
                    MessageFactory.text(f"Hi {profile.name}")
                )
                await turn_context.send_activity(
                    MessageFactory.text("What is your email id?")
                )
                flow.last_question_asked = Question.EMAIL

       # validate email then ask for mobile number
        elif flow.last_question_asked == Question.EMAIL:
            validate_result = self._validate_email(user_input)
            if not validate_result.is_valid:
                await turn_context.send_activity(
                    MessageFactory.text(validate_result.message)
                )
            else:
                profile.age = validate_result.value
                await turn_context.send_activity(
                    MessageFactory.text(f"I have your email id  as {profile.email}.")
                )
                await turn_context.send_activity(
                    MessageFactory.text("When is your Mobile number?")
                )
                flow.last_question_asked = Question.MOBILENUMBER

        # validate mobile number then ask for pincode
        elif flow.last_question_asked == Question.MOBILENUMBER:
            validate_result = self._validate_mobile(user_input)
            if not validate_result.is_valid:
                await turn_context.send_activity(
                    MessageFactory.text(validate_result.message)
                )
            else:
                profile.age = validate_result.value
                await turn_context.send_activity(
                    MessageFactory.text(f"I have your mobile number as {profile.mobilenumber}.")
                )
                await turn_context.send_activity(
                    MessageFactory.text("Which city you want to know the covidh details?")
                )
                flow.last_question_asked = Question.CITYNAME

        # validate pincode and wrap it up
        elif flow.last_question_asked == Question.CITYNAME:
            validate_result = self._validate_cityname(user_input)
            if not validate_result.is_valid:
                await turn_context.send_activity(
                    MessageFactory.text(validate_result.message)
                )
            else:
                profile.date = validate_result.value
                await turn_context.send_activity(
                    MessageFactory.text(
                        f"You have entered the city name as  {profile.cityname}."
                    )
                )
                await turn_context.send_activity(
                    MessageFactory.text(
                        f"Thanks for providing the details {profile.name}."
                    )
                )
                await turn_context.send_activity(
                    MessageFactory.text("Type anything to run the bot again.")
                )
                flow.last_question_asked = Question.NONE

    def _validate_name(self, user_input: str) -> ValidationResult:
        if not user_input:
            return ValidationResult(
                is_valid=False,
                message="Please enter a name that contains at least one character.",
            )

        return ValidationResult(is_valid=True, value=user_input)

    def _validate_mobile(self, user_input: str) -> ValidationResult:
        if not user_input:
            return ValidationResult(
                is_valid=False,
                message="Please enter valid number.",
            )

        return ValidationResult(is_valid=True, value=user_input)

    def _validate_email(self, user_input: str) -> ValidationResult:
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if(re.search(regex,user_input)): 
            return ValidationResult(is_valid=True, value=user_input)
        return ValidationResult(
            is_valid=False, message="Please enter valid email id"
        )

    def _validate_cityname(self, user_input: str) -> ValidationResult:
        if not user_input:
            return ValidationResult(
                is_valid=False,
                message="Please enter a city name that contains at least one character.",
            )

        return ValidationResult(is_valid=True, value=user_input)
    
