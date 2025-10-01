# Direct test to see the actual content of .env file
with open('.env', 'rb') as f:
    content = f.read()
    print("Raw bytes of .env file:")
    print(repr(content))
    print()
    print("Decoded content:")
    print(repr(content.decode('utf-8')))
    
print("\nNow reading line by line:")
with open('.env', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        print(f"Line {i}: {repr(line)}")