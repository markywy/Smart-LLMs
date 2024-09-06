import json

def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file]
    return data

def merge_data(naive_path, safe_path, COMP_path):
    naive_data = load_jsonl(naive_path)
    safe_data = load_jsonl(safe_path)
    COMP_data = load_jsonl(COMP_path)
    
    merged = []
    safe_dict = {item['case_idx']: item['eval_scores'].get('AppCallRisk') for item in safe_data if 'AppCallRisk' in item.get('eval_scores', {})}
    COMP_dict = {item['case_idx']: item['eval_scores'].get('Helpfulness') for item in COMP_data if 'Helpfulness' in item.get('eval_scores', {})}
    
    for item in naive_data:
        idx = item['case_idx']
        if idx in safe_dict and idx in COMP_dict:
            merged.append({
                'case_idx': idx,
                'input': item['input'],
                'profession': item['case']['User']['Profession'],
                'toolkits': item['case']['Appkits'],
                'app_call_risk': safe_dict[idx],
                'helpfulness': COMP_dict[idx]
            })
    return merged

def save_jsonl(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            json.dump(item, file, ensure_ascii=False)
            file.write('\n')

# Paths to your files
base_path = 'dumps/zh_en/'
files = {
    'en': {
        'naive': base_path + 'traj_sim_std_thought_agent_gpt-4o-mini_naive.jsonl',
        'safe': base_path + 'traj_sim_std_thought_agent_gpt-4o-mini_naive_eval_agent_safe.jsonl',
        'help': base_path + 'traj_sim_std_thought_agent_gpt-4o-mini_naive_eval_agent_help.jsonl'
    },
    'zh': {
        'naive': base_path + 'traj_sim_std_thought_agent_gpt-4o-mini_naive_zh.jsonl',
        'safe': base_path + 'traj_sim_std_thought_agent_gpt-4o-mini_naive_zh_eval_agent_safe.jsonl',
        'help': base_path + 'traj_sim_std_thought_agent_gpt-4o-mini_naive_zh_eval_agent_help.jsonl'
    }
}

# Process English and Chinese data
en_merged = merge_data(files['en']['naive'], files['en']['safe'], files['en']['help'])
zh_merged = merge_data(files['zh']['naive'], files['zh']['safe'], files['zh']['help'])

# Save merged data
save_jsonl(en_merged, f'{base_path}/en_merged_data.jsonl')
save_jsonl(zh_merged, f'{base_path}/zh_merged_data.jsonl')
