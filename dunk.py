import pytesseract
from PIL import Image
import openai
from faker import Faker
from faker.providers import address
from nltk.corpus import wordnet
import random
import cv2
import numpy as np
import poe
import time

# webby
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import nltk
import re
nltk.download('wordnet')    

# Create a Faker object
fake = Faker()
fake.add_provider(address)

# GPT MODEL SETUP
# OpenAI GPT-4
try:
    with open("openai_token.txt", "r") as f:
        openai.api_key = f.read()
except:
    print("Unable to find openai_token.txt! Please place a txt file in the folder with your api access key!")

poe_key = ""
poe_client = None
# POE API
try:
    with open("poe_token.txt", "r") as f:
        poe_key = f.read()
        poe_client = poe.Client(poe_key)
        print(poe_client.bot_names)
except:
    print("Unable to find poe_token.txt! Please place a txt file in the folder with your api access key!")

if openai.api_key == "" or poe_key == "":
    print("Please place a txt file in the folder with your api access key! The script cannot work without it!!")


def random_address():
    for i in range(1000): # Badcode 
        try:
            data = fake.address()
            address = data[:data.index('\n')]

            # Extract the city (from after the newline character up to the comma)
            city = data[data.index('\n')+1:data.index(',')]

            part_data = data.split('\n')
            part_data = part_data[1].split(',')
            part_data = part_data[1].split(" ")
            # Extract the state (from after the comma up to the ZIP code)
            state = part_data[1]

            # Extract the ZIP code (from after the state to the end of the string)
            zipcode = part_data[2]
            if state == "MO":
                return address, city, state, zipcode
        except:
            pass
    print("Failed to generate suitable address!")

def random_names():
    first_name = fake.first_name()
    last_name = fake.last_name()
    return first_name, last_name

def random_email():
    email_start = fake.email()
    email_end = fake.free_email_domain()
    email_start = email_start.split("@")[0]
    email = email_start + "@" + email_end
    return email


def random_adjective():
    # Get all synsets for adjectives
    adj_synsets = list(wordnet.all_synsets(pos='a'))

    # Get all lemmas for adjectives
    adj_lemmas = [lemma for synset in adj_synsets for lemma in synset.lemmas()]

    # Get all names for adjectives
    adjectives = [lemma.name() for lemma in adj_lemmas]

    # Select a random adjective
    random_synset = random.choice(list(adj_synsets))
    adjective = random_synset.name().split('.')[0]

    print(f"I'm feeling {adjective}")
    return adjective


def generate_details_openai(first_name, last_name, address, city, state, zipcode):
    mood = random_adjective()
    initial_prompt = f"You are a bot designed to write reporting letters to law agencies about trans harassment. Write the letter in a {mood} style, but keep it somewhat professional. The event took place in Missouri. Keep all your responses under 500 characters."
    full_history = [{"role": "system", "content": initial_prompt}] + [{"role": "user", "content": f"Write a letter pretending to be {first_name} {last_name}, from the address {address}, {city}, {state}, {zipcode} "}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=full_history,
        temperature=0.6,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    ai_response = response['choices'][0]['message']['content']
    if "[Law enforcement agency]" in ai_response:
        ai_response = ai_response.replace("[Law enforcement agency]", "Andrew Bailey")
    if "[" in ai_response:
        ai_response = ai_response.replace("[", "")
    if "]" in ai_response:
        ai_response = ai_response.replace("]", "")
    if "Drugs" in ai_response:
        ai_response = ai_response.replace("Drugs", "Estrogen")
    print(ai_response)
    return ai_response

def generate_details_free(first_name, last_name, address, city, state, zipcode, poe_client):
    if poe_client == None:
        with open("poe_token.txt", "r") as f:
            poe_key = f.read()
            poe_client = poe.Client(poe_key)
    
    mood = random_adjective()
    initial_prompt = f"Write a letter pretending to be {first_name} {last_name}, from the address {address}, {city}, {state}, {zipcode} to a law agency about trans harrassment in a {mood} style. The event took place in Missouri. Keep your response below 500 characters."
    ai_response = ""
    for chunk in poe_client.send_message("capybara", initial_prompt, with_chat_break=True):
        print(chunk["text_new"], end="", flush=True)
        ai_response += chunk["text_new"]
    if "[Law enforcement agency]" in ai_response:
        ai_response = ai_response.replace("[Law enforcement agency]", "Andrew Bailey")
    if "[" in ai_response:
        ai_response = ai_response.replace("[", "")
    if "]" in ai_response:
        ai_response = ai_response.replace("]", "")
    if "Drugs" in ai_response:
        ai_response = ai_response.replace("Drugs", "Estrogen")
    #delete the 3 latest messages, including the chat break
    poe_client.purge_conversation("capybara", count=3)
    return ai_response

def remove_isolated_pixels(image, connectivity, iterations = 5, thresh = 1):
    for _ in range(iterations):
        nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=connectivity)
        sizes = stats[:, -1]
        img2 = np.zeros(output.shape, dtype=np.uint8)
        for i in range(1, nb_components):
            if sizes[i] > thresh:
                img2[output == i] = 255
        image = img2
    return img2

def bold_letters(img):
    pixdata = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][0] < 90:
                pixdata[x, y] = (0, 0, 0, 255)
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][1] < 136:
                pixdata[x, y] = (0, 0, 0, 255)
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][2] > 0:
                pixdata[x, y] = (255, 255, 255, 255)
    return img

def solve_captcha2(image_name, no_chars = 5, x_letter_width = 30, buffer=10):
    
    # Opening the Image, convertring to grayscale
    image = Image.open(image_name).convert("L")
    # covert pixels to either be black or white
    # thresholding
    for column in range(0, image.height):
        for row in range(0, image.width):
            if image.getpixel((row, column)) > 128:
                image.putpixel((row, column), 255)
            else:
                image.putpixel((row, column), 0)
    pixel_matrix = image.load()
    
    # thresholding 2???
    for column in range(0, image.height):
        for row in range(0, image.width):
            if pixel_matrix[row, column] != 0:
                pixel_matrix[row, column] = 255

    # stray line and pixel removal
    for column in range(1, image.height - 1):
        for row in range(1, image.width - 1):
            if pixel_matrix[row, column] == 0 \
                and pixel_matrix[row, column - 1] == 255 and pixel_matrix[row, column + 1] == 255:
                pixel_matrix[row, column] = 255
            if pixel_matrix[row, column] == 0 \
                and pixel_matrix[row - 1, column] == 255 and pixel_matrix[row + 1, column] == 255:
                pixel_matrix[row, column] = 255

    image.save("lessnoise_image1.png")

    config = "--oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    captcha = pytesseract.image_to_string(image, config=config)[:5]
    # Remove any extra spaces
    captcha = captcha.replace(" ", "")
    # remove anything that isn't a letter or a number
    captcha = re.sub("[^a-zA-Z0-9]", "", captcha)
    # make uppercase
    captcha = captcha.upper()

    if captcha == "":
        print("capatcha FAILED!")

    print(captcha)
    return captcha

def solve_captcha(image_name, sigma=0.3):
    # Load the image
    img = Image.open(image_name)
    
    # Make the letters bolder for easier recognition
    img = bold_letters(img)

    # Convert the PIL Image object to a NumPy array
    img_array = np.array(img)

    # Save the image to a temporary file
    img.save("input-black.gif", "GIF")

    #scaled_img = cv2.resize(img_array, (img_array.shape[1] * 5, img_array.shape[0] * 5), interpolation=cv2.INTER_LINEAR)

    # Convert the OpenCV image to a PIL Image object
    #pil_image = Image.fromarray(cv2.cvtColor(scaled_img, cv2.COLOR_BGR2RGB))

    # Save the image to a temporary file
    #pil_image.save("input-black.gif", "GIF")

    return solve_captcha2("input-black.gif", 5)


def fill_in_form(fname, lname, address, city, state, zipcode, email, phone, letter):
    url = 'https://ago.mo.gov/file-a-complaint/transgender-center-concerns'

    # Initialize a new browser instance
    driver = webdriver.Chrome()
    # Navigate to the form page
    driver.get(url)
    # Wait for the captcha image to be visible
    wait = WebDriverWait(driver, 10)  # Adjust the timeout (10 seconds here) as needed
    captcha_img = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'img[data-sf-role="captcha-image"]')))

    # Get the binary data of the captcha image
    captcha_data = captcha_img.screenshot_as_png
    # Write the binary data to a file
    with open('captcha.png', 'wb') as f:
        f.write(captcha_data)

    captcha = solve_captcha2("captcha.png")
    # Fill in the form fields

    driver.find_element(By.NAME, 'TextFieldController_4').send_keys(fname)
    driver.find_element(By.NAME, 'TextFieldController_5').send_keys(lname)
    driver.find_element(By.NAME, 'TextFieldController_1').send_keys(address)
    driver.find_element(By.NAME, 'TextFieldController_2').send_keys(city)
    Select(driver.find_element(By.NAME, 'DropdownListFieldController')).select_by_value(state)
    driver.find_element(By.NAME, 'TextFieldController_6').send_keys(zipcode)
    driver.find_element(By.NAME, 'TextFieldController_0').send_keys(email)
    driver.find_element(By.NAME, 'TextFieldController_3').send_keys(phone)
    driver.find_element(By.NAME, 'ParagraphTextFieldController').send_keys(letter)
    driver.find_element(By.NAME, 'captcha-a').send_keys(captcha)
    
    # Submit the form
    #driver.find_element(By.XPATH, '//button[@type="submit"]').click()

    # Close the browser
    time.sleep(10)
    driver.quit()

while True:
    # Generate names
    fname, lname = random_names()
    address, city, state, zipcode = random_address()
    email = random_email()

    # Generate letter
    print(f"Generating letter for {fname} {lname} ({email}) at {address}, {city}, {state}, {zipcode}")
    letter = ""
    if poe_key:
        letter = generate_details_free(fname, lname, address, city, state, zipcode, poe_client)
    elif openai.api_key != "":
        letter = generate_details_openai(fname, lname, address, city, state, zipcode)
    else:
        print("Setup was incorrectly followed!! Please follow the readme!!")
    # Fill in form
    fill_in_form(fname, lname, address, city, state, zipcode, email, "", letter)

    time.sleep(10)
