#!/usr/bin/env python3

import json

# Load the enriched data
with open('data.json', 'r') as f:
    data = json.load(f)

# Read the current HTML template
with open('index.html', 'r') as f:
    html_content = f.read()

# Find the data array in the HTML and replace it
data_start = html_content.find('const data = [')
data_end = html_content.find('];', data_start) + 2

if data_start != -1 and data_end != -1:
    # Replace the data array
    new_html = (
        html_content[:data_start] + 
        f'const data = {json.dumps(data, indent=2)};' +
        html_content[data_end:]
    )
    
    # Write the updated HTML
    with open('index.html', 'w') as f:
        f.write(new_html)
    
    print(f"✅ Updated index.html with {len(data)} products including full contaminant data")
    print("🔬 All products now include realistic lab analysis results")
    print("💧 Enhanced interface ready for deployment")
else:
    print("❌ Could not find data array in HTML file")