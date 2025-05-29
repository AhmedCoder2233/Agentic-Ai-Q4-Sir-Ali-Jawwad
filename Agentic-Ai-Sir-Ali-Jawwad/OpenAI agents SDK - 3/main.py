import requests
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, Runner
from dotenv import load_dotenv
import chainlit as cl
import os

load_dotenv()

api_key_weather = os.getenv("WEATHER_API_KEY")

api_key = os.getenv("GEMINI_API_KEY")

provider = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)


@function_tool("weather")
def getWeather(city: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key_weather}&units=metric"

    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"Weather in {city}: {weather}, Temperature: {temp}°C"
    else:
        return f"Failed to get weather for {city}. Status code: {response.status_code}"


agent = Agent(
    name="Weather Agent",
    instructions="You're a weather agent if user ask for weather of any specific city use the weather tool to give the answer beyond weather if user ask for any other thing tell him that i was just for weather",
    model=model,
    tools=[getWeather]
)

@cl.on_chat_start
async def chatStart():
    await cl.Message(content="Welcome to the Weather Agent!").send()

@cl.on_message
async def userChat(message: cl.Message):
    response = Runner.run_sync(agent, message.content)
    await cl.Message(content=response.final_output).send()