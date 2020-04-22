
import pyowm
from config.config_reader import ConfigReader
import plotly.graph_objects as go
import pandas as pd
import requests
import io
from flask import Flask,render_template
from flask_mail import Mail, Message
import json
import logging
import os
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class CovidhDetails():
    def __init__(self):
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()
        


    def get_covidh_info(self,city):
        self.city=city

        ## Country Search
        try:
            url = "https://www.trackcorona.live/api/countries.csv"
            data=requests.get(url).content
            ds = pd.read_csv(io.StringIO(data.decode('utf-8')))
            df = ds.apply(lambda x: x.astype(str).str.upper())
        except:
            self.bot_says = "Data extraction site is under maintenca please comee again 20 minutes later. Sorry for the inconvenience caused."
            return self.bot_says

        searchinput = city

        data = df.loc[df["location"]==searchinput.upper()]
        citysearch = False;
        if data.empty == True:
            self.get_covidh_city_info(city)
        else:
            self.bot_says = "As of today in " + city +":\n Confirmed cases :"+data['confirmed'].to_string(index=False)+ " Recovered "+data['recovered'].to_string(index=False)+  " Dead :" + data['dead'].to_string(index=False) + " Last Updated :" + data['updated'].to_string(index=False)+""
        return self.bot_says

    def get_covidh_city_info(self,city):
        self.city=city
        try:
            url = "https://www.trackcorona.live/api/cities.csv"
            data=requests.get(url).content
            ds = pd.read_csv(io.StringIO(data.decode('utf-8')))
            df = ds.apply(lambda x: x.astype(str).str.upper())
            searchinput = city
            data = df.loc[df["location"]==searchinput.upper()]
        except:
            self.bot_says = "Data extraction site is under maintenca please comee again 20 minutes later. Sorry for the inconvenience caused."
            return self.bot_says

        if data.empty == True:
            self.bot_says = "No Data"
        else:
            self.bot_says = "As of today in " + city +":\n Confirmed cases :"+data['confirmed'].to_string(index=False)+ " Recovered "+data['recovered'].to_string(index=False)+  " Dead :" + data['dead'].to_string(index=False) + " Last Updated :" + data['updated'].to_string(index=False)+""
        return self.bot_says

    def sendMail(self,toAddress, username):
        #smpt configuration
        try:
            sendto = 'auromirapps@gmail.com'
            user= 'auromirapps@gmail.com'
            password = "foryoureyesonly@9696"
            smtpsrv = "smtp.office365.com"
            smtpserver = smtplib.SMTP(smtpsrv,587)

            smtpserver.starttls()
            smtpserver.ehlo
            smtpserver.login(user, password)

            #message template creation
            msg = MIMEMultipart() 
            
            # setup the parameters of the message
            msg['From']="auromirapps@gmail.com"
            msg['To']= toAddress
            msg['Subject']="Coronavirus - Preventive measures"
            emailcontent = "<p><h3>Dear "+username+",</h3></p>"
            emailcontent = emailcontent +"""\
            

            <p>
                In January, we established a multi-functional coronavirus response task force and are following the current guidance from government and local health authorities.

            </p>

            <p>

                To prevent the spread of COVID-19:<br />
                Clean your hands often. Use soap and water, or an alcohol-based hand rub.<br />
                Maintain a safe distance from anyone who is coughing or sneezing.<br />
                Don’t touch your eyes, nose or mouth.<br />
                Cover your nose and mouth with your bent elbow or a tissue when you cough or sneeze.<br />
                Stay home if you feel unwell.<br />
                If you have a fever, a cough, and difficulty breathing, seek medical attention. Call in advance.<br />
                Follow the directions of your local health authority.<br />
            </p>
            <p>Best Regards,</p>
            <p>Gypsy Bots Team</p>

            """
            
            # add in the message body
            

            msg.attach(MIMEText(emailcontent, 'html'))

            # send the message via the server set up earlier.
            smtpserver.send_message(msg)
            del msg
            smtpserver.quit()
        except:
            self.bot_says = "Email was not sent due to connectivy issues"
            return self.bot_says

#Generate world corona map
    def renderWorldCoronaMap(self):
        url = "https://www.trackcorona.live/api/countries.csv"
        data=requests.get(url).content
        ds = pd.read_csv(io.StringIO(data.decode('utf-8')))
        df = ds.apply(lambda x: x.astype(str).str.upper())
        maxval = int(df["confirmed"].max())
        #chart
        df['text'] = df['location'] +"\n Confirmed cases :"+ df["confirmed"]
                
        fig = go.Figure(data = go.Scattergeo(
            lon = df["longitude"],
            lat = df["latitude"],
            text = df["text"],
            mode = "markers",
            marker = dict(
                size = 12,
                opacity = 0.8,
                reversescale = True,
                autocolorscale = True,
                symbol = 'square',
                line = dict(
                    width = 1,
                    color = 'rgba(102, 102, 105)'
                ),
                cmin = 0,
       
                cmax = maxval,
                colorbar_title = "COVID 19 Reported Cases"
            )
        ))
        fig.update_layout(
            title = "COVID19 Confirmed Cases Around the World",
            geo = dict(
                scope = "world",
                showland = True,
            )
        )
        worldmapfile = 'templates/index.html'
        fig.write_html(worldmapfile)



            






