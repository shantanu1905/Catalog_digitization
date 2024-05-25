from dotenv import load_dotenv
from app.logger import Logger
import langchain_google_genai 
import os
import json


log = Logger()
logger = log.get_logger(__name__)
load_dotenv()

#Gemini free trial 15 request per minutes
gemini_api_key=os.getenv("GEMINI_API_KEY")



# Set up Google Generative AI (replace with your actual API key)
llm = langchain_google_genai.ChatGoogleGenerativeAI(
    model="gemini-pro", temperature=0.3, google_api_key=gemini_api_key
)


def     process_user_input(user_input):
  """Processes user text input to extract product names.
  Args:
      user_input: User's text input (e.g., "add maggi noodles, add Horlicks").
  Returns:
      A list of product names extracted from the user input.
  """

  product_names = []
  words = user_input.lower().split()  # Convert to lowercase and split into words
  # Identify product names using heuristics (can be improved based on your use case)
  for i in range(len(words)):
    if words[i] == "add" and (i + 1 < len(words)):
      product_names.append(words[i + 1])
  return product_names



def extract_info(product_data):
    lines = product_data.split('\n\n')
    info = {}
    for line in lines:
        if '**Product Name:**' in line:
            info['name'] = line.replace('**Product Name:**', '').strip()
        elif '**Brand:**' in line:
            info['brand'] = line.replace('**Brand:**', '').strip()
        elif '**Category:**' in line:
            info['category'] = line.replace('**Category:**', '').strip()
        elif '**ASIN_Number:**' in line:
            info['ASIN_Number'] = line.replace('**ASIN Number:**', '').strip()
        elif '**Description:**' in line:
            info['description'] = line.replace('**Description:**', '').strip()
        elif '**Price:**' in line:
            info['price'] = line.replace('**Price:**', '').strip()
    return info

def generate_product_info(product_names):
  """Generates product information using Google Generative AI.

  Args:
      product_names: A list of product names to research.

  Returns:
      A list of dictionaries containing product information in JSON format.
  """

  product_info = []
  for product_name in product_names:
    # Craft a more informative prompt, potentially including category hints
    prompt = f"You are a knowledgeable e-commerce assistant. The user wants to add the following product: '{product_name}'. Please provide a comprehensive description of the product, including its full name, brand, category, ASIN number (if available), price (if available)."

    # Generate product information using Google Generative AI
    response = llm.invoke(prompt)
    response = response.content

    # Extract and format information from the response (structure can vary based on response format)
    try:
      product_info.append(response)    
      extracted_data = [extract_info(item) for item in product_info ]  
    except KeyError:
      print(f"Warning: Could not extract all information for product: {product_name}")  # Handle potential missing data


  return extracted_data