import json
import argparse
import random

def filter_data(input_file, output_file, sample_num):
    # Load the JSON data from the file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Filter the list of dictionaries
    standard = 'AppCallRisk' if 'safe' in input_file else 'Helpfulness'
    bad_data = [x for x in data if x.get('eval_scores', {}).get(standard) in ["0", "1"]]
    good_data = [x for x in data if x.get('eval_scores', {}).get(standard) in ["2", "3"]]
    selected_data = random.sample(bad_data, sample_num) + random.sample(good_data, sample_num)

    # Save the filtered data back to a new JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(selected_data, file, indent=4, ensure_ascii=False)

    # Print or use the filtered data
    print(f"Random unsafe data has been saved to {output_file}")

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Random JSON data based on AppCallRisk score.')
    parser.add_argument('--input-path', '-inp', type=str, help='The path to the input JSON file.', default='assets/all_traj_gpt_4o_eval_agent_safe.json')
    parser.add_argument('--sample-num', "-num", type=int, help="Num of random samples", default=50)

    # Parse the command line arguments
    args = parser.parse_args()
    output_file = args.input_path.replace('traj_', 'selected_')
    # Call the filter_data function with the provided file paths
    filter_data(args.input_path, output_file, args.sample_num)

if __name__ == '__main__':
    main()