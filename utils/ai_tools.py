from openai import AsyncOpenAI
from groq import AsyncGroq, GroqError
from utils.data import Configs
import ollama
import os
import openai
import requests
import re

THIS_PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.dirname(THIS_PATH)

class TextModel:

    def __init__(self):
        self.config = Configs().config
        self.openai_client = AsyncOpenAI(api_key=self.config['GPT_TOKEN'])
        self.groq_client = AsyncGroq(api_key=self.config["GROQ"],)



    async def getLLM(self, prompt, modelName):
        try:
            options = ollama.Options(temperature=float(".6"), stop=['[INST', '[/INST', '[END]'],)
            response = ollama.chat(model=modelName, messages=prompt, options=options)
            result = response['message']['content'].strip()

            if "[END]" not in result:
                return result + " [END]"
            result = re.sub(r'\*.*?\*', '', result)
            return result
        except requests.exceptions.RequestException as e:
            return False, f"{e}"




    async def getGPT(self, prompt, modelName):
        """Using openai's GPT API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=modelName, # gpt-4-1106-preview, gpt-4-turbo, gpt-4-turbo-2024-04-09, gpt-3.5-turbo-1106, gpt-3.5-turbo-16k
                max_tokens=200,
                temperature=0.6,
                stop='[END]',
                messages=prompt
            )

            # Remove everything after [END] but still append it to the end of the msg
            # This is so the AI still attempts to generate [END] for every msg.
            response = response.choices[0].message.content + " [END]"
            response = re.sub(r'\*.*?\*', '', response)
            return response
        except openai.APIConnectionError as e:
            return False, "The server could not be reached"
        except openai.RateLimitError as e:
            return False, "A 429 status code was received; we should back off a bit."
        except openai.APIStatusError as e:
            return False, "Another non-200-range status code was received"




    async def getGroq(self, prompt, modelName):
        """Using Groq's API to quickly use large models"""
        try:
            response = await self.groq_client.chat.completions.create(
                model=modelName, # mixtral-8x7b-32768, llama2-70b-4096, gemma-7b-it, llama3-70b-8192
                max_tokens=200,
                temperature=0.6,
                stop=['[INST', '[/INST', '[END]'],
                messages=prompt
            )

            # Remove everything after [END] but still append it to the end of the msg
            # This is so the AI still attempts to generate [END] for every msg.
            response = response.choices[0].message.content.strip() + " [END]"
            response = re.sub(r'\*.*?\*', '', response)
            return response
        except GroqError as e:
            return False, f"An error occurred: {e}"




    async def hasProfanity(self, words):
        """Checks if a word/sentence is Inappropriate"""
        response = await self.openai_client.moderations.create(input=words)
        return response.results[0].flagged