"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
import asyncio  
import sys  
from flask import Flask, request, Response  
from botbuilder.core import (  
    BotFrameworkAdapter,  
    BotFrameworkAdapterSettings,     
    TurnContext,      
) 
from botbuilder.schema import Activity  
from echobot import*  

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

bot = EchoBot()  
  
SETTINGS = BotFrameworkAdapterSettings("","")  
ADAPTER = BotFrameworkAdapter(SETTINGS) 

LOOP = asyncio.get_event_loop()  

@app.route("/api/messages", methods=["POST"]) 

def messages():  
    if "application/json" in request.headers["Content-Type"]:  
        body = request.json  
    else:  
        return Response(status=415)  
  
    activity = Activity().deserialize(body)  
    auth_header = (  
        request.headers["Authorization"] if "Authorization" in request.headers else ""  
    )  
  
    async def aux_func(turn_context):  
        await bot.on_turn(turn_context)  
  
    try:  
        task = LOOP.create_task(  
            ADAPTER.process_activity(activity, auth_header, aux_func)  
        )  
        LOOP.run_until_complete(task)  
        return Response(status=201)  
    except Exception as exception:  
        raise Response(status=405)  



if __name__ == '__main__':
    app.run()
