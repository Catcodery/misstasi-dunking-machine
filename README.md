# misstasi-dunking-machine
Dunking on the nazis

This "helps" missouri by providing them with reports of transphobia to their Transgender Center Concerns Form automatically.

It uses AI! How hip and cool.

# How to use
 You're gonna need a few things:
 - Python
 - Pytessaract
 - Either an openai API key, or a poe API key. Poe is free, openai is not.

# Installing python
- Go to the official Python website: https://www.python.org/downloads/
- Click the "Download Python" button, and select the appropriate version for your operating system.
- Run the installer file once it is downloaded, and follow the installation wizard prompts to complete the installation process.
- Once the installation is complete, you can open a command prompt or terminal window, and type python to verify that Python has been installed correctly.

# Installing pytessaract
## Install Tesseract OCR:
- For Windows: Download the installer from Tesseract's GitHub releases page and install it. The recommended installer for Windows is from the University of Mannheim.
- For macOS: Use Homebrew to install Tesseract by running brew install tesseract.
- For Linux: Use the package manager for your distribution to install Tesseract. For example, on Ubuntu, run sudo apt install tesseract-ocr.

## Add Tesseract to your system's PATH:
### For Windows:
- Locate the folder where Tesseract was installed (usually C:\Program Files\Tesseract-OCR).
- Press the Windows key, type "Environment Variables" and open "Edit the system environment variables".
- Click on the "Environment Variables" button.
- In the "System variables" section, find and select the "Path" variable, then click "Edit".
- Click "New" and add the path to the Tesseract installation folder (e.g., C:\Program Files\Tesseract-OCR).
- Click "OK" to save your changes.
- 
### For macOS and Linux: 
The Tesseract executable is usually installed in a folder already included in the system's PATH (e.g., /usr/local/bin), so you may not need to make any changes.

Restart your IDE or terminal to ensure that the updated PATH is used.

# API keys:
## Openai:
- Log in here: https://platform.openai.com/overview
- Click on your name on the top right and go to profile
- Click API keys on the left
- Generate new
- Create a new file called "openai_token.txt" and paste the key in there. Save the fie in the same folder as this repo on your computer.
- You **Will** need money on your account, though it's not too expensive.

## Poe
- See here: https://github.com/ading2210/poe-api#finding-your-token
- Paste the token in a new file called "poe_token.txt". Save the fie in the same folder as this repo on your computer.
- Poe is free

# Running it
- Open a terminal where the files are
- Type `python dunk.py`
- It should work
- Run it other ways too if you like

# Problems
- Captacha is a little wonky sometimes
- I didn't really review my code

# Disclaimer
- No warranties are given using this code, use at your own risk
- Consider using a VPN
- This is for academic uses ;)
