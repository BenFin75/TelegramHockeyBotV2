FROM arm32v7/python:3.10

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN git clone -b testing https://github.com/BenFin75/TelegramHockeyBotV2.git

WORKDIR /TelegramHockeyBotV2

CMD ["python3", "/TelegramHockeyBotV2/main.py"]