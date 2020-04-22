
from botbuilder.ai.luis import LuisApplication,LuisPredictionOptions,LuisRecognizer
import json
import re
import uuid
from config.config_reader import ConfigReader
from logger.logger import Log
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
import plotly.graph_objects as go
import pandas as pd
import requests
import io
import os
from botbuilder.core import CardFactory, MessageFactory
from botbuilder.schema import (
    ActionTypes,
    Attachment,
    AnimationCard,
    AudioCard,
    HeroCard,
    VideoCard,
    ReceiptCard,
    SigninCard,
    ThumbnailCard,
    MediaUrl,
    CardAction,
    CardImage,
    ThumbnailUrl,
    Fact,
    ReceiptItem,
    AttachmentLayoutTypes,
)



from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    TurnContext,
    UserState,
    MessageFactory,
)

from data_models import ConversationFlow, Question, UserProfile
from pandemic.covidh import CovidhDetails


class ValidationResult:
    def __init__(
        self, is_valid: bool = False, value: object = None, message: str = None
    ):
        self.is_valid = is_valid
        self.value = value
        self.message = message

class LuisConnect(ActivityHandler):
    def __init__(self,conversation_state: ConversationState, user_state: UserState):
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()
        self.luis_app_id=self.configuration['LUIS_APP_ID']
        self.luis_endpoint_key = self.configuration['LUIS_ENDPOINT_KEY']
        self.luis_endpoint = self.configuration['LUIS_ENDPOINT']
        self.luis_app = LuisApplication(self.luis_app_id,self.luis_endpoint_key,self.luis_endpoint)
        self.luis_options = LuisPredictionOptions(include_all_intents=True,include_instance_data=True)
        self.luis_recognizer = LuisRecognizer(application=self.luis_app,prediction_options=self.luis_options,include_api_results=True)

        self.log=Log()
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
 

    async def on_message_activity(self,turn_context:TurnContext):
        # Get the state properties from the turn context.
        profile = await self.profile_accessor.get(turn_context, UserProfile)
        flow = await self.flow_accessor.get(turn_context, ConversationFlow)
        try:
            await self._fill_out_user_profile(flow, profile, turn_context)
        except:
             self.log.error('Failed to do something: ')


        # Save changes to UserState and ConversationState
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)
  



    async def _fill_out_user_profile(
        self, flow: ConversationFlow, profile: UserProfile, turn_context: TurnContext
    ):
        try:
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
                    profile.email = validate_result.value
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
                    profile.mobilenumber = validate_result.value
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
                    profile.cityname = validate_result.value
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
                    partionkey = str(uuid.uuid4())
                    rowid=str(uuid.uuid4())
                    username = profile.name
                    emailid= profile.email
                    mobile = profile.mobilenumber
                    city = profile.cityname
               
                    #fig.show()
                    #save data to cosmos table
                    table_service = TableService(connection_string='DefaultEndpointsProtocol=https;AccountName=gypsycosmostable;AccountKey=dXx6HK61qvIJpzdQsCLbCpEnUd7szCAf5cWNVkeXk4ExZHqxjip7MeFQCBSBgNUhXiIvfoyPQky2tT0bzKzlFQ==;TableEndpoint=https://gypsycosmostable.table.cosmos.azure.com:443/;')
                    userdetails = {'PartitionKey': partionkey, 'RowKey': rowid, 'name': username, 'emailid': emailid,'city':city}
                    table_service.insert_entity('gypsybotconversations', userdetails)
                    #get corona virus details
                    covidh_info=CovidhDetails()
                    luis_result = await self.luis_recognizer.recognize(turn_context)
                    result = luis_result.properties["luisResult"]
                    covidh=covidh_info.get_covidh_info(profile.cityname)
                
                            
                    await turn_context.send_activity(f"{covidh}")
                    # Send email to User about prventive measures
                    covidh_info.sendMail(emailid,username)
                    await turn_context.send_activity(
                        MessageFactory.text("we have sent all covid-19 cases report in detail and prevention measure to your mail.")
                    )
                    
                    
                    message = MessageFactory.list([])
                    message.attachments.append(self.create_hero_card())
                    await turn_context.send_activity(message)
                    #await turn_context.send_activity(
                    #    MessageFactory.text(f"Please clear to look the demograph of corona virus across the world : {worldmap}")
                    #)
                    

                    flow.last_question_asked = Question.NONE
        except:
            await turn_context.send_activity(
                        MessageFactory.text("Something went wrong please contact the administrator.")
                    )



    #Validations for inputs
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
        else:
            covidh_info=CovidhDetails()
            covidh=covidh_info.get_covidh_info(user_input)
            if covidh=="No Data":
                return ValidationResult(
                is_valid=False,
                message="Sorry no data available for the city / country name you have provide. Plesae try once again")

        return ValidationResult(is_valid=True, value=user_input)
    #cards
    def create_hero_card(self) -> Attachment:
        card = HeroCard(
            title="Covidh Coronavirus cases worldwide",
            images=[
                CardImage(
                    url="https://static.businessinsider.sg/2020/03/03/5e6f8ee1c48540116e247a42.png"
                )
            ],
            buttons=[
                CardAction(
                    type=ActionTypes.open_url,
                    title="Click Here",
                    value="https://bing.com/covid?form=msntrk",
                )
            ],
        )
        return CardFactory.hero_card(card)
    
   