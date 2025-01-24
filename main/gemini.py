from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import google.generativeai as genai
import re
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, TooManyRequests, NotTranslatable, TranslationLanguageNotAvailable
import sys
import traceback

genai.configure(api_key="AIzaSyBAFeFgmjem2W-VFQeIYP-orMwDza_EOqA")


def get_method(id):
    try:
        list = YouTubeTranscriptApi.list_transcripts(id)
        available_language = []
        for obj in list:
            available_language.append(obj.language_code)
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id=id)
            transcript = transcript_list.find_transcript([available_language[0]])
            translated = transcript.translate("en").fetch()
            text =TextFormatter().format_transcript(translated)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"""
                https://www.youtube.com/watch?v={id}

                Extract the ingredients and method. Format the ingredients as a Python list of tuples, where each tuple is (ingredient_name, quantity). Format the method as a Python list of strings, where each string is a step.

                For example:

                Ingredients:
                [("flour", "2 cups"), ("sugar", "1 cup"), ("eggs", "2")]

                Method:
                ["Preheat oven to 350F", "Mix flour and sugar", "Add eggs and mix well"]
                """)

            print("there is the response" + response.text)
            return extract_ingredients_and_method(response.text)
    except TranscriptsDisabled as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("An unexpected error occurred:")
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        ingredients = []
        method = []
        return ingredients, method
    except NoTranscriptFound as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("An unexpected error occurred:")
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        ingredients = []
        method = []
        return ingredients, method
    except VideoUnavailable as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("An unexpected error occurred:")
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        ingredients = []
        method = []
        return ingredients, method
    except TooManyRequests as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("An unexpected error occurred:")
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        ingredients = []
        method = []
        return ingredients, method






def extract_ingredients_and_method(text):
    """
    Extracts ingredients and method lists from a text containing Python list definitions.

    Args:
        text: The input text containing the Python list definitions.

    Returns:
        A tuple containing the ingredients list and the method list. 
        Returns (None, None) if either list is not found or parsing fails.
    """

    try:
        # Extract ingredients
        ingredients_match = re.search(r"ingredients\s*=\s*\[(.*?)\]", text, re.DOTALL)
        if ingredients_match:
            ingredients_str = ingredients_match.group(1)
            # Improved parsing to handle various tuple formats
            ingredients = eval(f"[{ingredients_str}]")
            #check if it's a list of tuple, if not make it a list of tuple
            if not all(isinstance(item, tuple) for item in ingredients):
                ingredients = [tuple(item) if isinstance(item, list) else (item,) for item in ingredients]
        else:
            ingredients = []

        # Extract method
        method_match = re.search(r"method\s*=\s*\[(.*?)\]", text, re.DOTALL)
        if method_match:
            method_str = method_match.group(1)
            method = eval(f"[{method_str}]")
            #check if it's a list of string, if not make it a list of string
            method = [str(item) for item in method]
        else:
            method = []

        return ingredients, method

    except (SyntaxError, NameError, TypeError, ValueError) as e:
        print(f"Error parsing the text: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [], []