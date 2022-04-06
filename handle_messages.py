from telegram import *
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# handles sending the message to the user
def send(updater, chat_id, message):
    if (type(message) == list):
            for n in message:
                if (type(n) != str):
                    send_image(updater, chat_id, n)
                else:
                        send_message(updater, chat_id, n)
        
    elif (type(message) != str):
        send_image(updater, chat_id, message)
    else:
        send_message(updater, chat_id, message)

def send_message(updater, chat_id, message):
    updater.bot.send_message(
        chat_id, text=message, disable_web_page_preview=1)

def send_image(updater, chat_id, table):

    table_string = str(table)
    n = 0
    max_length = 0
    for i in table:
        length = int(len(str(i))/7)
        if length > max_length:
            max_length = length
        n += 1
    width = (max_length-2)*10
    height = (125 + ((n)*21))
    
    
    out = Image.new("RGB", (width, height), ('#182533'))

    # get a font
    fnt = ImageFont.truetype('./JetBrainsMono-Bold.ttf', 15)
    # get a drawing context
    d = ImageDraw.Draw(out)

    # draw multiline text
    d.multiline_text((15, 4), table_string, font=fnt, fill=('#e4ecf2'))
    
    out.save('./Database/image.png')
    updater.bot.send_photo(chat_id, photo=open('./Database/image.png', 'rb'))