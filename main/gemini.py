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
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id=id)
        available_transcripts = {}
        available_transcripts.update(transcript_list._generated_transcripts)
        available_transcripts.update(transcript_list._manually_created_transcripts)
        print("============Available Transcripts=================")
        print(print(available_transcripts))
        print("============Generated Transcripts=================")
        print(print(transcript_list._generated_transcripts))
        print("============Manually Created Transcripts=================")
        print(print(transcript_list._manually_created_transcripts))
        print("============Available Languages=================")
        print(transcript_list._translation_languages)
        starting_list = ['en', 'en-GB', 'en-US', 'en-IN']
        final_list = starting_list + list(transcript_list._manually_created_transcripts.keys()) + list(transcript_list._generated_transcripts.keys())
        print("============Final List=================")
        print(final_list)
        transcript = transcript_list.find_transcript(list(available_transcripts.keys()))
        # print(transcript.language)
        # print(transcript.language_code)
        # print(transcript.translation_languages)
        ingredients = []
        method = []
        return ingredients , method

        if transcript.language_code not in ['en', 'en-GB', 'en-US', 'en-IN']:
            if "en" in transcript.translation_languages:
                transcript = transcript.translate('en').fetch()
            elif "en-GB" in transcript.translation_languages:
                transcript = transcript.translate('en-GB').fetch()
            elif "en-US" in transcript.translation_languages:
                transcript = transcript.translate('en-US').fetch()
            elif "en-IN" in transcript.translation_languages:
                transcript = transcript.translate('en-IN').fetch()
            else:
                transcript = transcript.fetch()

        else:
            transcript = transcript.fetch()
            print(transcript)
        text =TextFormatter().format_transcript(transcript)
        print(text)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"""
            

                Extract the ingredients and method from {text}. Format the ingredients as a Python list of tuples, where each tuple is (ingredient_name, quantity). Use @ to enclose the tuples  like @(..,..)@ and , to separate them and use " to enclose ingredient and quantity and , to separate them. Format the method as a Python list of strings, where each string is a step.Alway use # to enclose the steps like #..# and , to separate them.

                For example:

                Ingredients:
                [@("flour", "2 cups")@, @("sugar", "1 cup")@, @("eggs", "2")@]

                Method:
                [#"Preheat oven to 350F"#, #"Mix flour and sugar"#, #"Add eggs and mix well"#]
                """)
        print(response.text)

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
        ingredient_pattern = r'@\((.*?)\)@'
        tuples = re.findall(ingredient_pattern, text)
    
        # Extract individual ingredients from each tuple
        ingredients = [tuple(re.findall(r'"([^"]*)"', t)) for t in tuples]


        # Extract method
        pattern = r'#"(.*?)"#'
        steps = re.findall(pattern, text)

        return ingredients, steps

    except (SyntaxError, NameError, TypeError, ValueError) as e:
        print(f"Error parsing the text: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [], []


def validate_search(search):
    """
    Validates the search query to ensure it is a valid recipe item.

    Args:
        search: The search query to validate.

    Returns:
        True if the search query is a valid YouTube video ID, False otherwise.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"""
            Validate the search query "{search}" to ensure it is a food item. Return True if it is a possible food item, False otherwise also make sure true and false are always separate from the nearby words by a space.
            """)
        print("there is the response" + response.text)
        return 'true' in response.text.lower()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    
    