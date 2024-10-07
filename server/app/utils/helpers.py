import re
from server.app.utils.constants import question_words

def get_source_indeces_from_chat(input_string):
    try:
        # Define the pattern to match the SOURCES_USED part
        pattern = r'\*\*SOURCES_USED: \[(.*?)\]\*\*'
        
        # Search for the pattern in the input string
        match = re.search(pattern, input_string)
        
        if match:
            # Extract the numbers part and convert them to a list of integers
            numbers_str = match.group(1)
            numbers = list(map(int, numbers_str.split(',')))
            
            # Remove the SOURCES_USED part from the original string
            trimmed_string = re.sub(pattern, '', input_string).strip()
            
            return numbers, trimmed_string
        else:
            # If the pattern is not found, return an empty list and the original string
            return [], input_string.strip()
    except Exception as e:
        # In case of any exceptions, return an empty list and the original string
        return [], input_string.strip()
    
def title_query_string(query):
    # Split the query into words
    words = query.split()
    
    # Function to capitalize only the first letter of each word
    def capitalize_first_letter(words):
        return ' '.join(word.capitalize() for word in words)
    
    # Generate all combinations
    def generate_versions(words):
        combined = ' '.join(words)

        # Create variations
        versions = set()

        # Original combined string and lowercase version
        versions.add(combined)
        versions.add(combined.lower())

        # Capitalize first letter of each word
        combined_cap = capitalize_first_letter(words)
        versions.add(combined_cap)
        versions.add(combined_cap.lower())

        # Capitalize first letter of first word and lowercase others
        if len(words) > 1:
            first_cap_rest_low = ' '.join([words[0].capitalize()] + [word.lower() for word in words[1:]])
            versions.add(first_cap_rest_low)
            versions.add(first_cap_rest_low.lower())

            first_low_rest_cap = ' '.join([words[0].lower()] + [word.capitalize() for word in words[1:]])
            versions.add(first_low_rest_cap)
            versions.add(first_low_rest_cap.lower())

        # Replace punctuation characters with space
        combined_replaced = re.sub(r"[',.\-]", ' ', combined)
        replaced_words = combined_replaced.split()
        replaced_combined = ' '.join(replaced_words)
        versions.add(replaced_combined)
        versions.add(replaced_combined.lower())
        versions.add(capitalize_first_letter(replaced_words))
        versions.add(capitalize_first_letter(replaced_words).lower())

        # Remove punctuation characters
        combined_removed = re.sub(r"[',.\-]", '', combined)
        removed_words = combined_removed.split()
        removed_combined = ' '.join(removed_words)
        versions.add(removed_combined)
        versions.add(removed_combined.lower())
        versions.add(capitalize_first_letter(removed_words))
        versions.add(capitalize_first_letter(removed_words).lower())

        return versions
    
    # Generate the LIKE clauses
    like_clauses = [f"title like '%{version}%'" for version in generate_versions(words)]
    
    # Combine all LIKE clauses with OR
    return ' or '.join(like_clauses)

def is_question(string):
    string = string.lower()
    for word in question_words:
        if word in string:
            return True
    return False