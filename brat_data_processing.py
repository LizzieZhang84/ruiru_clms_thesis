import json
import sys

def process_json_file(json_file_path):
    # Read the JSON data from the file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract the encounter_id
    encounter_id = data["encounter_id"]

    # Prepare the text content
    text_content = []

    # Include author_id and post_title_edited
    main_author_id = data['author_id']
    post_title_edited = data['post_title_edited']
    text_content.append(f"author_id: {main_author_id}")
    text_content.append(f"title: {post_title_edited}")

    # Include the first post content_edited
    first_post = data['thread'][0]['content_edited']
    text_content.append(f"post: {first_post}")

    # Include content_edited from the rest of the thread if content_edited is not None or NaN
    for entry in data['thread'][1:]:
        if entry['keep'] == 1 and entry['content_edited'] is not None and not isinstance(entry['content_edited'], float):
            author_id = entry['author_id']
            content_edited = entry['content_edited']
            if author_id == main_author_id:
                print("Poster's reply exist!")
                text_content.append(f"#POSTER# {author_id}: {content_edited}")
            else:
                text_content.append(f"{author_id}: {content_edited}")

    # Join the text content with newlines
    text_content_str = "\n---------------\n".join(text_content)

    # Write to a txt file named after the encounter_id
    filename = f"./round6/{encounter_id}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text_content_str)

    print(f"Content written to {filename}")

idx = sys.argv[1]
# Specify the path to your JSON file
json_file_path = f'../project2-medQA-data/mediqa-m3/valid/ENC009{idx}/ENC009{idx}.json'

# Process the JSON file
process_json_file(json_file_path)
