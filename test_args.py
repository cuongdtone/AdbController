import datetime
import requests
from urllib.request import urlretrieve
from pathlib import Path
import yaml
import sys
import uuid
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os

IMAGE_API = 'http://192.168.1.41:8000/api/files/'
filename = '0906317392_1656471566_noti.jpg'

medias = [filename]

for filename in medias:
    img_url = IMAGE_API + filename
    try:
        if requests.request('GET', img_url).status_code == 200:
            a = urlretrieve(img_url, "src/imgs/a.jpg")
        else:
            print('not found')

    except Exception as exc:
        _, _, exc_tb = sys.exc_info()
        print("download_image: %s - %s - Line: %d" % (img_url, exc, exc_tb.tb_lineno))

# url = IMAGE_API[:-1] + "-upload"
# header = {
#     # "Authorization": TOKEN
# }
#
#
# img = Image.open(os.path.join('src/screenshots', filename))
# byte_io = BytesIO()
# img.save(byte_io, 'PNG')
# byte_io.seek(0)
#
# payload = {}
# files = [('files', (filename, byte_io, 'image/png'))]
#
# response = requests.request("POST", url=url, data=payload, files=files, headers=header)
# print(response)



