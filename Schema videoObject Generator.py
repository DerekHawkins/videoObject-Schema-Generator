
# coding: utf-8

# In[ ]:


from genson import SchemaBuilder
import dateutil.parser as parser
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from selenium import webdriver

video_data = pd.read_excel(#Path to your excel file)
youtube = video_data['Video URL']
link = video_data['Embed URL']

### Gathers Thumbnail Image from YouTube ###
def Thumbnail_Pull(url):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    cpath= 'C:\\Webdriver\\chromedriver'
    driver = webdriver.Chrome(options=options,executable_path=cpath)
    driver.get((url))
    url_main = driver.current_url
    driver.quit()
    i_id = url_main.replace('https://www.youtube.com/watch?v=', '').replace('&feature=youtu.be', '')
    thumbnail = 'https://img.youtube.com/vi/' + i_id + '/sddefault.jpg'
    return thumbnail

### Scrapes Video Title, Description and Date of Publishing for Vide
### Converts Date to ISO format
def YouTube_Data_Crawl(url):
    data = []
    r = requests.get(url)
    content = r.content
    soup = BeautifulSoup(content, 'lxml')
    # Title
    try:
        title = soup.select('.watch-title')
        title = title[0].getText()
        title = title.strip().replace('\n',' ')
    except IndexError:
        title = 'null'
    # Description
    try:
        des = soup.find('p', {'id': 'eow-description'})
        description = des.text
        description = description.replace('\n', '-').replace('\r', ' ').replace('\t', ' ').replace('"', '')
    except (IndexError, AttributeError) as e:
        description = 'null'
    # Date
    try:
        dates = soup.find('div', {'id': 'watch-uploader-info'})
        date_fake = dates.text.replace('Published on ', '').replace('Uploaded on ', '')
        date = parser.parse(date_fake)
        date = date.isoformat()
    except (IndexError, ValueError) as e:
        date = 'null'
    data.append((title, description, date))
    return data

### Schema Build ###
def SchemaBuild(des, name, date, thumbnailURL, embedded):
    builder = SchemaBuilder()
    builder.add_schema({"@type": "VideoObject"})
    builder.add_schema({"description": des})
    builder.add_schema({"name": name})
    builder.add_schema({"thumbnailUrl": thumbnailURL})
    builder.add_schema({"uploadDate": date})
    builder.add_schema({"embedUrl": embedded})
    meta_data = builder.to_schema()
    meta_data['$schema'] = 'http://schema.org'
    meta_data["@context"] = meta_data['$schema']
    del meta_data['$schema']
    meta = json.dumps(meta_data)
    return meta

frames = []
for video, embedded in zip(youtube, link):
    img = Thumbnail_Pull(url=video)
    vid_data = YouTube_Data_Crawl(url=video)
    df_main = pd.DataFrame(vid_data, columns=['Title', 'Description', "Date"])
    title = df_main['Title'].iloc[0]
    description = df_main['Description'].iloc[0]
    date = df_main['Date'].iloc[0]
    metadata = SchemaBuild(des=description, name=title, thumbnailURL=img, date=date, embedded=embedded)
    frames.append(metadata)

### Separate Raw File Save ###
    
#data_list = pd.DataFrame(frames, columns=['VideoObject Schema'])
#data_list['Video'] = youtube
#data_list.to_excel('schema_data_raw.xlsx')


video_data['Video Meta Data'] = data_list['VideoObject Schema']
video_data.to_excel(#final output)

