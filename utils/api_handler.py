# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 29/06/2022

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

config = yaml.load(open("src/config.yaml", 'r', encoding='utf-8'), Loader=yaml.FullLoader)
IMAGE_API = config['IMAGE_API']

font = ImageFont.truetype('src/font.ttf', 50, encoding='utf-8')


def download_image(medias=None):
    '''
        Download hình ảnh từ server
    '''
    if medias is None:
        medias = []
    for filename in medias:
        img_url = IMAGE_API + filename
        try:
            if requests.request('GET', img_url).status_code == 200:
                urlretrieve(img_url, os.path.join('src/imgs', filename))
        except Exception as exc:
            _,_, exc_tb = sys.exc_info()
            print("download_image: %s - %s - Line: %d" % (img_url, exc, exc_tb.tb_lineno))


def upload_image(image_data: BytesIO, filename: str):
    """
        Upload hình ảnh lên server
    """
    try:
        url = IMAGE_API[:-1] + "-upload"
        header = {
            # "Authorization": TOKEN
        }
        payload = {}

        files = [('files', (filename, image_data, 'image/png'))]

        response = requests.request("POST", url=url, data=payload, files=files, headers=header)
        print(response)
        if response.status_code == 200:
            return filename
        return None
    except Exception as exc:
        _,_, exc_tb = sys.exc_info()
        print("upload_image: %s - Line: %d" % (exc, exc_tb.tb_lineno))
        return None


def add_corners(im, rad=15):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def upload_image_from_path(img_path, account_id):
    img = Image.open(os.path.join('src/screenshots', img_path))
    w, h = img.size
    wText, hText = font.getsize(account_id)
    temp = Image.new('RGB', (wText + 20, hText + 20), (0, 0, 0))
    ImageDraw.Draw(temp).text((10, 10), account_id, 'white', font)
    temp = add_corners(temp)
    img.paste(temp, ((w // 2) - (wText + 20) // 2, h - 80), temp)
    byte_io = BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    filename = upload_image(byte_io, img_path)
    if filename is not None:
        os.remove(os.path.join('src/screenshots', img_path))
    print(filename)