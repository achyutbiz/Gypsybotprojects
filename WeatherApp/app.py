import asyncio  
import sys 
from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, ConversationState,MemoryStorage
from botbuilder.schema import Activity
import asyncio
from luis.luisApp import LuisConnect
import os
from logger.logger import Log

app = Flask(__name__)
loop = asyncio.get_event_loop()

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

bot_settings = BotFrameworkAdapterSettings("2e784c7e-30d4-4b0f-94a9-e363db97e6ca", "hA]5aBrRAxfpI-QISwco2emX[wp6?l9R")
bot_adapter = BotFrameworkAdapter(bot_settings)

#CON_MEMORY = ConversationState(MemoryStorage())
luis_bot_dialog = LuisConnect()


@app.route("/")
def chatbotInit():
    return "Welcome to Chatbot Project"

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["content-type"]:
        log=Log()
        request_body = request.json
        user_says = Activity().deserialize(request_body)
        log.write_log(sessionID='session1',log_message="user says: "+str(user_says))
        authorization_header = (request.headers["Authorization"] if "Authorization" in request.headers else "")

        async def call_user_fun(turncontext):
            await luis_bot_dialog.on_turn(turncontext)

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

