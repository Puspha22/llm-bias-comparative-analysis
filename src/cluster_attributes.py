from sentence_transformers import SentenceTransformer, util
import json
import re
import os
import csv

def load_attributes(path):
    print(f"Loading data from {path}...")
    attrs = set()
    vals_map = {}
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    prompt = data.get('prompt', '')
                    for p_line in prompt.split('\n'):
                        match = re.search(r'^\s+(\w+):\s+(\w+)', p_line)
                        if match: attrs.add(match.group(1))
                        
                        v_match = re.search(r'^\s+#\s+(\w+)\s+\[(.*?)\]', p_line)
                        if v_match:
                            k, v_str = v_match.groups()
                            vals = [v.strip().strip("'\"") for v in v_str.split(',') if v.strip()]
                            if k not in vals_map: vals_map[k] = set()
                            vals_map[k].update(vals)
                except: continue
    except:
        print("Error reading file.")
        
    return sorted(list(attrs)), vals_map

def main():
    dataset_path = os.path.join("data", "dataset", "prompts_expanded_new.jsonl")
    attributes, vals_map = load_attributes(dataset_path)
    
    print("Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Clustering attributes...")
    embeddings = model.encode(attributes, convert_to_tensor=True)
    clusters = util.community_detection(embeddings, min_community_size=1, threshold=0.75)
    
    print(f"Found {len(clusters)} clusters.")
    
    # Export
    rows = []
    for cluster in clusters:
        members = [attributes[i] for i in cluster]
        canonical = sorted(members, key=len)[0]
        
        for m in sorted(members):
            vals = ", ".join(sorted(list(vals_map.get(m, []))))
            rows.append([canonical, m, len(members), vals])
            
    out_file = os.path.join("reports", "attribute_clusters.csv")
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Canonical Name", "Attribute", "Cluster Size", "Values"])
        writer.writerows(rows)
        
    print(f"Saved to {out_file}")

if __name__ == "__main__":
    main()
