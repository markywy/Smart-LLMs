import json
import argparse
from smartllm.utils import read_file

def filter_data(input_file, num_file, output_file):
    # Load the JSON data from the file
    data = read_file(input_file)
    traj = read_file(num_file)
    # Filter the list of dictionaries
    numbers = [x["case_idx"] for x in traj]
    locate_data = [x["case"] for x in data if x.get('case_idx') in numbers]

    # Save the filtered data back to a new JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(locate_data, file, indent=4, ensure_ascii=False)

    # Print or use the filtered data
    print(f"Selected data has been saved to {output_file}")

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Filter JSON data based on AppCallRisk score.')
    parser.add_argument('--input-path', '-inp', type=str, help='The path to the input JSON file.', default='assets/all_traj_gpt_4o_zh.json')
    parser.add_argument("--selected-path", '-sp', type=str, help="The path to the selected case number")

    # Parse the command line arguments
    args = parser.parse_args()

    output_file = args.selected_path.replace("_eval", "")
    # Call the filter_data function with the provided file paths
    filter_data(args.input_path, args.selected_path, output_file=output_file)

if __name__ == '__main__':
    main()