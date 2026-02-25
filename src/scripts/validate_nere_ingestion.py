import json
import os

# Mocking the datasets library behavior for simulation purposes
class MockDataset:
    def __init__(self, data):
        self.data = data

    def map(self, function):
        # HuggingFace map applies function to each element
        new_data = [function(item) for item in self.data]
        return MockDataset(new_data)

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

def load_dataset(format, data_files, split='train'):
    print(f"Loading dataset from {data_files}...")
    data = []
    with open(data_files, 'r') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return MockDataset(data)

# The User's provided code logic
def build_oqm_dataset():
    # ADJUSTED PATH for the simulation script location
    dataset_path = os.path.join(os.path.dirname(__file__), '../data/abrahamic_locution.jsonl')

    # Loads the JSONL file into the HuggingFace Dataset format (Simulated)
    dataset = load_dataset('json', data_files=dataset_path, split='train')

    # Format prompts for causal language modeling using Llama-3 Chat Template
    def format_prompt(example):
        return {"text": f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are the IHCEI NERE v4.0 Cognitive Mirror. You operate exclusively using the Abrahamic Locution.<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{example['instruction']}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
{example['response']}<|eot_id|>"""}

    formatted_dataset = dataset.map(format_prompt)
    return formatted_dataset

def main():
    print("--- Task 1: Code & Syntax Validation ---")
    print("Validating JSONL structure and Python mapping function logic...")
    # (The execution itself validates the logic)

    print("\n--- Task 2: Dry-Run Output Generation ---")
    formatted_ds = build_oqm_dataset()

    # Print 2nd entry (index 1) - regarding '3arsh'
    print("\n[Entry 2: '3arsh']")
    print(formatted_ds[1]['text'])

    # Print last entry (index -1) - regarding 'Iblees'
    print("\n[Last Entry: 'Iblees']")
    print(formatted_ds[-1]['text'])

if __name__ == "__main__":
    main()
