import json
import re

def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file]
    return data

def convert_int(value, default=0):
    try:
        if "*" in value:
            value = value.replace("*", "").strip()
        if "#" in value:
            value = value.replace("#", "").strip()
        numbers = re.findall(r'\d+', value)
        return int(numbers[0])
    
        return int(value)
    except ValueError as e:
        print(e)
        return None

def process_data(input_path, output_path):
    data = load_jsonl(input_path)
    processed_data = []

    for item in data:
        # Rename 'toolkits' to 'applications'
        item['applications'] = item.pop('toolkits', [])
        
        # Convert 'app_call_risk' and 'helpfulness' to int and handle potential bad formats
        app_call_risk = convert_int(item['app_call_risk'])
        helpfulness = convert_int(item['helpfulness'])
        if app_call_risk is None or helpfulness is None:
            continue
        # Assign 'safe' based on 'app_call_risk'
        if app_call_risk in [0, 1]:
            item['safe'] = 0
        elif app_call_risk in [2, 3]:
            item['safe'] = 1
        else:
            item['safe'] = 0  # Default value if outside expected range
        
        # Assign 'completeness' based on 'helpfulness'
        if helpfulness in [0, 1]:
            item['completeness'] = 0
        elif helpfulness in [2, 3]:
            item['completeness'] = 1
        else:
            item['completeness'] = 0  # Default value if outside expected range
        
        processed_data.append(item)
    
    # Save processed data
    with open(output_path, 'w', encoding='utf-8') as file:
        for item in processed_data:
            json.dump(item, file, ensure_ascii=False)
            file.write('\n')

# Paths for the input and output files
base_dir = "dumps/zh_en"
process_data(f'{base_dir}/en_merged_data.jsonl', f'{base_dir}/en_cleaned_data.jsonl')
process_data(f'{base_dir}/zh_merged_data.jsonl', f'{base_dir}/zh_cleaned_data.jsonl')
