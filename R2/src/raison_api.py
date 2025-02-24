import requests
from private_information import *

# API headers
headers = {
    "x-api-key": api_key
}

def extract_elements_and_options(metadata):
    """
    Extracts labels and IDs of elements, as well as the IDs of options.

    Parameters:
        metadata (dict): Data containing 'elements' and 'options' sections.

    Returns:
        tuple:
            - A dictionary {label: id} for elements.
            - A list of dictionaries [{"id": id}] for options.
    """
    elems = {}  # Stores labels and IDs of elements
    opts = []   # Stores IDs of options

    # Retrieve elements and options
    elem_items = metadata.get('elements', [])
    opts_items = metadata.get('options', [])

    # Process elements and add their labels and IDs to the dictionary
    for item in elem_items:
        label = item.get("label")
        id_value = item.get("id")
        elems[label] = id_value

    # Process options and add their IDs to a list
    for item in opts_items:
        id_value = item.get("id")
        opts.append({"id": id_value})

    return elems, opts

def check_solutions(options):
    """
    Verifies valid solutions among the provided options.

    Parameters:
        options (list): List of options containing the 'isSolution' key.

    Returns:
        list: A list of valid option labels or None if none.
    """
    # List to store names of valid options
    true_options = []

    # Iterate through each option
    for option in options:
        if option['isSolution']:  # Check if 'isSolution' is True
            true_options.append(option['option']['label'])  # Add the label of the option

    # Return valid options or None if none
    return true_options if true_options else None

def get_data_api(url, api_key):
    """
    Retrieves data from the API and extracts labels and IDs.

    Parameters:
        url (str): The API URL.
        api_key (str): API key for authentication.

    Returns:
        metadata: Returned metadata
    """
    headers = {
        "x-api-key": api_key
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            metadata = response.json()
        elif response.status_code == 400:
            print("Error 400: Invalid request.")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return metadata

def call_api(scenario):
    """
    Calls the API to evaluate scenarios and returns valid options.

    Parameters:
        scenario (list): List of labels of elements to include in the scenario.

    Returns:
        list: Valid solutions or None if none.
    """
    metadata = get_data_api(url, api_key)
    elements, options = extract_elements_and_options(metadata)

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    ids = []

    # Prepare IDs of scenario elements
    for case in scenario:
        temp_dict = dict()
        temp_dict["id"] = elements[case]
        ids.append(temp_dict)

    payload = {
        "elements": ids,
        "options": options,
        "limit": len(options)
    }

    try:
        # Send the POST request with the JSON payload
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            metadata = response.json()
        elif response.status_code == 400:
            print("Error 400: Invalid request.")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Return valid solutions
    return check_solutions(metadata)
