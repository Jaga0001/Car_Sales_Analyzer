import spacy
from spacy.matcher import Matcher
import json
import os
import re

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize a matcher
matcher = Matcher(nlp.vocab)

# Define patterns for information extraction
patterns = {
    "CAR_TYPE": [
        [{"LOWER": "hatchback"}],
        [{"LOWER": "suv"}],
        [{"LOWER": "sedan"}],
        [{"LOWER": "convertible"}],
        [{"LOWER": "coupe"}],
        [{"LOWER": "wagon"}],
        [{"LOWER": "van"}],
        [{"LOWER": "jeep"}]
    ],
    "FUEL_TYPE": [
        [{"LOWER": "petrol"}],
        [{"LOWER": "diesel"}],
        [{"LOWER": "electric"}],
        [{"LOWER": "hybrid"}],
        [{"LOWER": "gas"}]
    ],
    "TRANSMISSION_TYPE": [
        [{"LOWER": "manual"}],
        [{"LOWER": "automatic"}],
        [{"LOWER": "semi-automatic"}],
        [{"LOWER": "cvt"}]
    ],
    "POLICIES": [
        [{"LOWER": "free"}, {"LOWER": "rc"}, {"LOWER": "transfer"}],
        [{"LOWER": "five"}, {"LOWER": "day"}, {"LOWER": "money"}, {"LOWER": "back"}, {"LOWER": "guarantee"}],
        [{"LOWER": "free"}, {"LOWER": "rsa"}, {"LOWER": "for"}, {"LOWER": "one"}, {"LOWER": "year"}],
        [{"LOWER": "return"}, {"LOWER": "policy"}]
    ],
    "OBJECTIONS": [
        [{"LOWER": "refurbishment"}, {"LOWER": "quality"}],
        [{"LOWER": "car"}, {"LOWER": "issues"}],
        [{"LOWER": "price"}, {"LOWER": "issues"}],
        [{"LOWER": "customer"}, {"LOWER": "experience"}, {"LOWER": "issues"}]
    ]
}

# Add patterns to the matcher
for label, pattern_list in patterns.items():
    matcher.add(label, pattern_list)

def read_text_files(directory_path):
    """
    Reads all text files from the specified directory and returns a dictionary 
    with filenames as keys and file content as values.
    
    Parameters:
        directory_path (str): Path to the directory containing text files.
    
    Returns:
        dict: A dictionary where the keys are filenames and the values are the file content.
    """
    data = {}
    
    # List all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a text file
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read the content of the file
                content = file.read()
                # Store the content in the dictionary
                data[filename] = content
    
    return data

def filter_customer_text(text):
    """
    Filters out only the customer text from the conversation.
    
    Parameters:
        text (str): The full conversation text.
    
    Returns:
        str: The filtered text containing only customer responses.
    """
    customer_lines = []
    lines = text.split('\n')
    for line in lines:
        if line.startswith("Customer:"):
            customer_lines.append(line.replace("Customer:", "").strip())
    return ' '.join(customer_lines)

def extract_information(text):
    """
    Extracts car-related information from the provided customer text.

    Parameters:
        text (str): The transcript text.

    Returns:
        dict: A dictionary containing extracted information.
    """
    doc = nlp(text)

    # Initialize output dictionary
    extracted_info = {
        "Customer Requirements": {
            "Car Type": None,
            "Fuel Type": None,
            "Color": extract_color(text),
            "Distance Travelled": extract_distance(text),
            "Make Year": extract_make_year(text),
            "Transmission Type": None,
            "Budget": extract_budget(text)
        },
        "Company Policies Discussed": {
            "Free RC Transfer": False,
            "5-Day Money Back Guarantee": False,
            "Free RSA for One Year": False,
            "Return Policy": False
        },
        "Customer Objections": {
            "Refurbishment Quality": False,
            "Car Issues": False,
            "Price Issues": False,
            "Customer Experience Issues": False
        }
    }

    # Run the matcher on the doc
    matches = matcher(doc)

    for match_id, start, end in matches:
        match_label = nlp.vocab.strings[match_id]
        match_text = doc[start:end].text.lower()

        # Fill in Customer Requirements
        if match_label == "CAR_TYPE":
            extracted_info["Customer Requirements"]["Car Type"] = match_text.capitalize()
        elif match_label == "FUEL_TYPE":
            extracted_info["Customer Requirements"]["Fuel Type"] = match_text.capitalize()
        elif match_label == "TRANSMISSION_TYPE":
            extracted_info["Customer Requirements"]["Transmission Type"] = match_text.capitalize()
        
        # Fill in Company Policies
        if match_label == "POLICIES":
            if "rc transfer" in match_text:
                extracted_info["Company Policies Discussed"]["Free RC Transfer"] = True
            elif "money back guarantee" in match_text:
                extracted_info["Company Policies Discussed"]["5-Day Money Back Guarantee"] = True
            elif "rsa for one year" in match_text:
                extracted_info["Company Policies Discussed"]["Free RSA for One Year"] = True
            elif "return policy" in match_text:
                extracted_info["Company Policies Discussed"]["Return Policy"] = True
        
        # Fill in Customer Objections
        if match_label == "OBJECTIONS":
            if "refurbishment quality" in match_text:
                extracted_info["Customer Objections"]["Refurbishment Quality"] = True
            elif "car issues" in match_text:
                extracted_info["Customer Objections"]["Car Issues"] = True
            elif "price issues" in match_text:
                extracted_info["Customer Objections"]["Price Issues"] = True
            elif "customer experience issues" in match_text:
                extracted_info["Customer Objections"]["Customer Experience Issues"] = True

    return extracted_info

def extract_color(text):
    """
    Extracts the color mentioned in the text.
    """
    color_keywords = ['red', 'blue', 'black', 'white', 'silver', 'grey', 'green', 'yellow', 'orange']
    for color in color_keywords:
        if color in text.lower():
            return color.capitalize()
    return None

def extract_distance(text):
    """
    Extracts the distance traveled mentioned in the text.
    """
    match = re.search(r'\b\d{1,3}(?:,\d{3})*\s?(km|kilometers|miles)\b', text, re.IGNORECASE)
    return match.group(0) if match else None

def extract_make_year(text):
    """
    Extracts the make year mentioned in the text.
    """
    match = re.search(r'\b(19|20)\d{2}\b', text)
    return match.group(0) if match else None

def extract_budget(text):
    """
    Extracts the budget mentioned in the text.
    """
    match = re.search(r'\bRs\.\s*\d+(?:,\d{3})*\b', text)
    return match.group(0) if match else None

def process_transcripts(transcripts):
    """
    Processes multiple transcripts and extracts information from each.

    Parameters:
        transcripts (dict): A dictionary with filenames as keys and transcript content as values.

    Returns:
        dict: A dictionary with filenames as keys and extracted information as values.
    """
    results = {}
    for filename, content in transcripts.items():
        customer_text = filter_customer_text(content)
        results[filename] = extract_information(customer_text)
    return results

# Example usage
directory_path = "dataset"  # Replace with the actual path to your text files
transcripts = read_text_files(directory_path)
results = process_transcripts(transcripts)

# Output the results as a JSON file
with open('extracted_info.json', 'w') as outfile:
    json.dump(results, outfile, indent=4)

print("Extraction complete. Results saved to 'extracted_info.json'.")