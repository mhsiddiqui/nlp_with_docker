from text_generator import GenerateUrduText
from tts.text_processor.number_strings import NumberStrings


def get_processed_data(text):
    all_number_strings = NumberStrings(text).get_number_strings()
    for string_type, number_strings in all_number_strings.items():
        if string_type == 'number':
            number_strings.sort(key=lambda s: -len(s))
        for string in number_strings:
            urdu_text = GenerateUrduText(string=string, string_type=string_type.lower()).generate_text()
            text = text.replace(string, urdu_text.decode('utf-8'))
    return text
