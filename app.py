from dotenv import load_dotenv
import os
import time
from datetime import datetime
import requests
import urllib3
import pystray
from PIL import Image, ImageDraw
import threading

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

tpc = os.getenv("TIMING_POINT_CODE")

def job():
    response = requests.get('https://v0.ovapi.nl/tpc/' + tpc, verify=False)
    data = response.json()
    dest_dept = []
    for item in data[tpc]['Passes'].values():
        dest_dept.append((
            str(item["LinePublicNumber"]) + " " + item["DestinationName50"],
            item["ExpectedDepartureTime"].split("T")[0],
            item["ExpectedDepartureTime"].split("T")[1][:5]
        ))
    dest_dept = sorted(dest_dept, key=lambda element: (element[0], element[1], element[2]))
    if not dest_dept:  
        return "No data"
    return f"{dest_dept[0][0]} {dest_dept[0][2]}"

def create_image(text):
    img = Image.new('RGB', (64, 64), color='black')
    d = ImageDraw.Draw(img)
    d.text((5, 20), text, fill='white')
    return img

# just some dummy values
start_hour = 7
end_hour = 24
interval = 3600

def update(icon):
    while True:
        now = datetime.now()
        if start_hour <= now.hour < end_hour:
            text = job()
            icon.icon = create_image(text)
            icon.title = text
            time.sleep(interval) 
        else:
            print("Outside working hours:", now.time())
            time.sleep(interval)

icon = pystray.Icon("bus", create_image("..."))
threading.Thread(target=update, args=(icon,), daemon=True).start()
icon.run()