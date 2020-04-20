
import pyowm
from config.config_reader import ConfigReader
import plotly.graph_objects as go
import pandas as pd
import requests
import io

class CovidhDetails():
    def __init__(self):
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()


    def get_covidh_info(self,city):
        self.city=city

        ## Country Search
        url = "https://www.trackcorona.live/api/countries.csv"
        data=requests.get(url).content
        ds = pd.read_csv(io.StringIO(data.decode('utf-8')))
        df = ds.apply(lambda x: x.astype(str).str.upper())
        searchinput = city

        data = df.loc[df["location"]==searchinput.upper()]
        citysearch = False;
        if data.empty == True:
            citysearch = True
        else:
            self.bot_says = "As of today in " + city +" is :\n Confirmed cases :"+str(data['confirmed'])+ " Recovered "+".\n Minimum Temperature :"+str(data['recovered'])+  "Dead :" + str(data['dead']) + ""
        return self.bot_says