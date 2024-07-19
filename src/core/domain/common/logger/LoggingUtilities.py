import matplotlib.pyplot as plt
import time
from datetime import datetime
from itertools import chain,cycle
from IPython.display import display_html

# Using graph_objects
import plotly.graph_objects as go

class Logger:
    last_time_logged = 0
    
    
    def __init__(self):
        self.isLogging = True
        pass
    
    def log_timely(self, text, every_x_seconds):
        if self.isLogging: 
            current = time.time()
            if current - self.last_time_logged > every_x_seconds:
                log(str(text))
                self.last_time_logged = time.time()
    
    def reset_logging_time(self):
        self.last_time_logged = time.time()
        
    def enable(self, isLogging):
        self.isLogging = isLogging
        
    def log(self, text):
        if self.isLogging:
            log(str(text))

# log function
def log(text):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    print("[" + dt_string + "] " + text)

    
# Definig auxiliar function to display dataframes
from IPython.display import display_html
from itertools import chain,cycle
def display_side_by_side(*args,titles=cycle([''])):
    html_str=''
    for df,title in zip(args, chain(titles,cycle(['</br>'])) ):
        html_str+='<th style="text-align:center"><td style="vertical-align:top">'
        html_str+=f'<h5>{title}</h5>'
        html_str+=df.render().replace('table','table style="display:inline"')
        html_str+='</td></th>'
    display_html(html_str,raw=True)