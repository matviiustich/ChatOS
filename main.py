import openai
import requests
import json
from datetime import datetime, timezone

from System import System

system = System()

userInput = input("user: ")
while userInput != "/quit":
    system.add_to_memory("user", userInput)
    system.create_completion()
    userInput = input("user: ")
