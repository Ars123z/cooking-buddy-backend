import google.generativeai as genai
import re

def translate_ingredients(text, lang):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"""
        {text} translate this to {lang} Format the ingredients as a Python list of tuples, where each tuple is (ingredient_name, quantity). Use @ to enclose the tuples  like @(..,..)@ and , to separate them and use " to enclose ingredient and quantity and , to separate them.:
    """)
    return response.text

def translate_method(text, lang):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"""
        {text} translate this to {lang} Format the method as a Python list of strings, where each string is a step.Ensure Clean and Extractable data:
    """)
    return response.text



    
def extract_ingredients(input_string):
    # Pattern to match content within @ and between quotes
    pattern = r'@\((.*?)\)@'
    tuples = re.findall(pattern, input_string)
    
    # Extract individual ingredients from each tuple
    ingredients = [tuple(re.findall(r'"([^"]*)"', t)) for t in tuples]
    
    return ingredients

def extract_method(input_string):
    # Use regex to find all steps enclosed in quotes
    pattern = r'"([^"]+)"'
    steps = re.findall(pattern, input_string)
    return steps

