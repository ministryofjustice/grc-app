# extract.py

import sys

def extract(row_name='Secret:', input_file='sample.txt', output_file=None):
    items = []

    with open(input_file, 'r') as f:
        for line in f:
            if row_name in line:
                value = line.split(row_name, 1)[1].strip()
                if value:
                    items.append(value)

    if output_file:
        with open(output_file, 'w') as out:
            for item in items:
                out.write(item + '\n')
    else:
        for item in items:
            print(item)

def extract_secrets(input_file, output_file=None):
    extract('Secret:', input_file, output_file)

def extract_fingerprints(input_file, output_file=None):
    extract('Fingerprint:', input_file, output_file)

# 👇 Add this block to allow CLI usage
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 extract.py [secrets|fingerprints] input_file [output_file]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    input_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    if mode == 'secrets':
        extract_secrets(input_file, output_file)
    elif mode == 'fingerprints':
        extract_fingerprints(input_file, output_file)
    else:
        print(f"Unknown mode: {mode}")