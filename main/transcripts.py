import requests
import json

def get_transcripts(id, language_code):
    url = f"https://www.youtube.com/watch?v={id}"
    response = requests.get(url)
    splitted_html = response.split("'captions:")
    captions_json = json.loads(
        splitted_html[1].split(',"videoDetails')[0].replace("\n", "")
    ).get("playerCaptionsTracklistRenderer")
    if captions_json is None:
        raise Exception("No captions found")
    if "captionTracks" not in captions_json:
            raise Exception("No captions found")
    
    translation_languages = [
        {
            "language": translation_language["languageName"]["simpleText"],
            "language_code": translation_language["languageCode"],
            }
        for translation_language in captions_json.get("translationLanguages", [])
        ]
    base_url = captions_json["captionTracks"][0]["baseUrl"]
    response = requests.get(base_url)
    transcript = response.text
    