from Models.System import System

system = System()

userInput = input("user: ")
while userInput != "/quit":
    system.memory.append({"role": "user", "content": userInput})
    system.create_completion()
    userInput = input("user: ")
