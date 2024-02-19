import json


def print_error(msg):
    print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(f'error:')
    print(msg)
    print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

def get_llm_response_as_json(out_text):
    try:
        output = json.loads(out_text)
    except:
        try:
            # nous-hermes has a unique format
            if 'Here is the JSON output' in out_text:
                out_text = out_text.replace('```', '```json')
            output = parse_json_within_markers(out_text)
            # mixtral sometimes uses escaped json
            if not output:
                output = parse_escaped_json(out_text)
        except Exception as e:
            print_error(f'[get_llm_response_as_json] error {e} trying to parse json for {out_text}')
            output = None
    return output

def parse_json_within_markers(text, start_marker="```json", end_marker="```"):
    """
    Parses the JSON content between specified markers in a given text.

    :param text: The text containing the JSON to be parsed.
    :param start_marker: The start marker indicating the beginning of JSON content.
    :param end_marker: The end marker indicating the end of JSON content.
    :return: Parsed JSON object or None if parsing fails or markers are not found.
    """
    try:
        # Find the start and end of the JSON content
        start_idx = text.index(start_marker) + len(start_marker)
        end_idx = text.index(end_marker, start_idx)

        # Extract and parse the JSON content
        json_content = text[start_idx:end_idx].strip()
        
        # Some LLM quirks
        json_content = json_content.replace('},}','}}')
        return json.loads(json_content)
    except (ValueError, json.JSONDecodeError) as e:
        # ValueError for index not found, JSONDecodeError for invalid JSON
        print_error(f'[parse_json_within_markers] error {e} for text {text}')
        return None


def parse_escaped_json(json_string):
    """
    Parses a JSON string that contains escaped characters.

    :param json_string: The JSON string with escaped characters.
    :return: The parsed JSON object.
    """
    try:
        # Replace escaped backslashes with normal backslashes
        corrected_json_string = json_string.replace("\\", "")
        corrected_json_string = corrected_json_string.replace('\_', '_')
        return json.loads(corrected_json_string)
    except json.JSONDecodeError as e:
        return None