import sys 
import traceback
from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, ConversationState,MemoryStorage,TurnContext,UserState
from botbuilder.schema import Activity,ActivityTypes
import asyncio
from luis.luisApp import LuisConnect
import os
from logger.logger import Log
from pandemic.covidh import CovidhDetails
from bots import CustomPromptBot

app = Flask(__name__)
loop = asyncio.get_event_loop()

# Make the WSGI interface available at the top level so wfastcgi can get it.

bot_settings = BotFrameworkAdapterSettings("2e784c7e-30d4-4b0f-94a9-e363db97e6ca", "hA]5aBrRAxfpI-QISwco2emX[wp6?l9R")
bot_adapter = BotFrameworkAdapter(bot_settings)

# Create MemoryStorage and state
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

#CON_MEMORY = ConversationState(MemoryStorage())
luis_bot_dialog = LuisConnect(CONVERSATION_STATE, USER_STATE)



# Set the error handler on the Adapter.
# In this case, we want an unbound method, so MethodType is not needed.
#bot_adapter.on_turn_error = on_error

# Create MemoryStorage and state
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)
@app.route('/maps/')
def projects():
    return render_template("maps/worldcorona.html", title = 'Covidh Coronavirus cases around world')
@app.route('/templates/')
def renderTemmplate():
    return render_template("templates/emailtemplate.html", title = 'Email Template')


@app.route("/")
def chatbotInit():
    covidh_info=CovidhDetails()
    covidh_info.renderWorldCoronaMap()
    return app.send_static_file('worldcorona.html')

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["content-type"]:
        log=Log()
        request_body = request.json
        user_says = Activity().deserialize(request_body)
        authorization_header = (request.headers["Authorization"] if "Authorization" in request.headers else "")

        async def call_user_fun(turncontext):
            response=await luis_bot_dialog.on_turn(turncontext)
            if response:
                return jsonify(data=response.body, status=response.status)
            return Response(status=201)

        task = loop.create_task(
            bot_adapter.process_activity(user_says, authorization_header, call_user_fun)
        )
        loop.run_until_complete(task)
        return ""
    else:
        return Response(status=406)  # status for Not Acceptable




if __name__ == '__main__':
    #app.run(port= 3978)
    app.run()

