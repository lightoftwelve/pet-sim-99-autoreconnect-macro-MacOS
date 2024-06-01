import hashlib
import os

def generate_file_hash(file_path, algorithm='sha256'):
    """Generate a hash for the given file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

def verify_file_hash(file_path, expected_hash, algorithm='sha256'):
    """Verify that the file hash matches the expected hash."""
    return generate_file_hash(file_path, algorithm) == expected_hash

def verify_hashes():
    files_to_verify = [
        'capture_coordinates_gui.py', 
        'colors.py'
    ]

    # Verify hashes
    for file_path in files_to_verify:
        hash_file_path = f"{file_path}.hash"
        if os.path.exists(file_path) and os.path.exists(hash_file_path):
            with open(hash_file_path, 'r') as hash_file:
                expected_hash = hash_file.read().strip()
            if verify_file_hash(file_path, expected_hash):
                print(f"Hash verification succeeded for {file_path}")
            else:
                print(f"Hash verification failed for {file_path}")
        else:
            print(f"Missing file or hash file: {file_path} / {hash_file_path}")

def main():
    files_to_hash = [
        'capture_coordinates_gui.py', 
        'colors.py'
    ]

    # Generate hashes
    for file_path in files_to_hash:
        if os.path.exists(file_path):
            file_hash = generate_file_hash(file_path)
            print(f"Hash for {file_path}: {file_hash}")
            with open(f"{file_path}.hash", 'w') as hash_file:
                hash_file.write(file_hash)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
    # Uncomment the line below to verify hashes
    # verify_hashes()
