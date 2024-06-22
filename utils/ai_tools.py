from openai import AsyncOpenAI
from groq import Groq, GroqError
from utils.data import Configs
import os
import openai
import requests

THIS_PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.dirname(THIS_PATH)

class TextModel:

    def __init__(self):
        self.config = Configs().config
        self.openai_client = AsyncOpenAI(api_key=self.config['GPT_TOKEN'])
        self.groq_client = Groq(api_key=self.config["GROQ"],)



    async def getLLM(self, prompt):
        options = {
            "options": {
                "temperature": 0.6,
                "stop": ['[INST', '[/INST', '[END]'],
                "num_ctx": Configs().getChatModelInfo["num_ctx"]
                }
        }


        response = requests.post(
            "http://localhost:11434/v1/chat/completions",
            json={"model": "llama3", "messages": prompt, "stream": False,
                "options": options["options"]},
        )

        try:
            response.raise_for_status()
            data = response.json()
            result = data["choices"][0]["message"]["content"] 

            if "[END]" not in result:
                return result + " [END]"
            return  result

        except requests.exceptions.RequestException as e:
            return False, f"{e}"




    async def getGPT(self, prompt):
        """Using openai's GPT API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o", # gpt-4-1106-preview, gpt-4-turbo, gpt-4-turbo-2024-04-09, gpt-3.5-turbo-1106, gpt-3.5-turbo-16k
                max_tokens=200,
                temperature=0.6,
                stop='[END]',
                messages=prompt
            )

            # Remove everything after [END] but still append it to the end of the msg
            # This is so the AI still attempts to generate [END] for every msg.
            response = response.choices[0].message.content + " [END]"
            return response
        except openai.APIConnectionError as e:
            return False, "The server could not be reached"
        except openai.RateLimitError as e:
            return False, "A 429 status code was received; we should back off a bit."
        except openai.APIStatusError as e:
            return False, "Another non-200-range status code was received"




    async def getGroq(self, prompt):
        """Using Groq's API to quickly use large models"""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192", # mixtral-8x7b-32768, llama2-70b-4096, gemma-7b-it, llama3-70b-8192
                max_tokens=200,
                temperature=0.6,
                stop=['[INST', '[/INST', '[END]'],
                messages=prompt
            )

            # Remove everything after [END] but still append it to the end of the msg
            # This is so the AI still attempts to generate [END] for every msg.
            response = response.choices[0].message.content + " [END]"
            return response
        except GroqError as e:
            return False, f"An error occurred: {e}"




    async def hasProfanity(self, words):
        """Checks if a word/sentence is Inappropriate"""
        response = await self.openai_client.moderations.create(input=words)
        return response.results[0].flagged