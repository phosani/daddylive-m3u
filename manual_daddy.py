import requests
import re
import base64
import subprocess
import os

# --- Configuration ---
CHANNEL_AUTH_FILE = "manual_key.dat"
OUTPUT_URLS_FILE = "manual_url.dat"

def get_and_decode_data_for_id(premium_id, output_file="manual_key.dat"):
    """
    Fetches data from a URL for a specific premium ID, extracts a base64 string, and decodes
    specific nested base64 values within it. It also extracts the CHANNEL_KEY, and
    writes all output to a specified file.
    """
    url = f"https://jxoxkplay.xyz/premiumtv/daddylivehd.php?id={premium_id}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "referer": "https://daddylivestream.com"
    }

    with open(output_file, 'w') as f:
        f.write(f"Processing ID: {premium_id}\n")
        f.write("=" * 50 + "\n")
        
        try:
            # 1. Fetch the webpage content
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # 2. Extract the CHANNEL_KEY and write to file
            channel_key_match = re.search(r'CHANNEL_KEY="(premium[0-9]+)"', response.text)
            if channel_key_match:
                f.write(f"CHANNEL_KEY: {channel_key_match.group(1)}\n\n")
            else:
                f.write("CHANNEL_KEY: Not found\n\n")
                return False

            # 3. Extract the main 292-character base64 string
            main_base64_match = re.search(r'"([A-Za-z0-9+/=]{292})"', response.text, re.DOTALL)

            if not main_base64_match:
                f.write("Error: 292-character base64 string not found.\n")
                return False

            main_base64_string = main_base64_match.group(1)

            # 4. Decode the main base64 string
            try:
                decoded_content = base64.b64decode(main_base64_string).decode('utf-8')
            except base64.binascii.Error as e:
                f.write(f"Error decoding the main base64 string: {e}\n")
                return False
            
            # 5. Find the nested base64 values
            b_ts_match = re.search(r'"b_ts":"([A-Za-z0-9+/=]+)"', decoded_content)
            b_rnd_match = re.search(r'"b_rnd":"([A-Za-z0-9+/=]+)"', decoded_content)
            b_sig_match = re.search(r'"b_sig":"([A-Za-z0-9+/=]+)"', decoded_content)

            # 6. Write the results to the file
            if b_ts_match:
                f.write(f"b_ts: {b_ts_match.group(1)}\n")
            else:
                f.write("b_ts: Not found\n")
                return False

            if b_rnd_match:
                f.write(f"b_rnd: {b_rnd_match.group(1)}\n")
            else:
                f.write("b_rnd: Not found\n")
                return False

            if b_sig_match:
                f.write(f"b_sig: {b_sig_match.group(1)}\n")
            else:
                f.write("b_sig: Not found\n")
                return False

            return True

        except requests.exceptions.RequestException as e:
            f.write(f"Error during the web request for ID {premium_id}: {e}\n")
            return False

def generate_auth_urls_from_channel_auth_file(file_path):
    """
    Reads manual_key.dat, extracts authentication parameters,
    decodes base64 values for b_ts, b_rnd, and b_sig,
    and generates a list of auth.php URLs.
    """
    auth_urls = []
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Regex to find all blocks of data for each channel
        pattern = re.compile(
            r'CHANNEL_KEY:\s*(premium[0-9]+)\s+'
            r'b_ts:\s*([A-Za-z0-9+/=]+)\s+'
            r'b_rnd:\s*([A-Za-z0-9+/=]+)\s+'
            r'b_sig:\s*([A-Za-z0-9+/=]+)',
            re.DOTALL
        )

        # Find all matches in the file content
        for match in pattern.finditer(content):
            channel_key = match.group(1)
            b_ts_base64 = match.group(2)
            b_rnd_base64 = match.group(3)
            b_sig_base64 = match.group(4)
            
            try:
                # Decode the base64 values
                auth_ts = base64.b64decode(b_ts_base64).decode('utf-8')
                auth_rnd = base64.b64decode(b_rnd_base64).decode('utf-8')
                auth_sig = base64.b64decode(b_sig_base64).decode('utf-8')

                # Construct the final URL
                base_url = "https://top2new.newkso.ru/auth.php"
                url = (f"{base_url}?channel_id={channel_key}"
                       f"&ts={auth_ts}"
                       f"&rnd={auth_rnd}"
                       f"&sig={auth_sig}")
                
                auth_urls.append(url)
                
            except Exception as decode_e:
                print(f"Warning: Base64 decoding or URL construction error for channel '{channel_key}': {decode_e}. Skipping this block.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it exists.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    return auth_urls

def execute_curl_commands_from_file(file_path):
    """
    Reads a file containing URLs and executes a curl -I command for each URL.
    """
    print(f"\nReading URLs from '{file_path}' and executing curl commands...\n")
    
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()] # Read non-empty lines
        
        if not urls:
            print(f"No URLs found in '{file_path}'. Exiting curl execution.")
            return

        for url in urls:
            print(f"Executing curl for: {url}")
            
            # Construct the curl command as a list of strings
            curl_cmd = [
                "curl", "-k", "-I",
                "-H", "user-agent: TiviMate/5.2.0 (Android 12)",
                "-H", "Host: top2new.newkso.ru",
                "-H", "origin: https://jxoxkplay.xyz",
                "-H", "referer: https://jxoxkplay.xyz/",
                url
            ]
            
            try:
                # Execute the curl command
                result = subprocess.run(curl_cmd, capture_output=True, text=True, check=False)
                
                # Check the return code
                if result.returncode == 0:
                    status_line = result.stdout.splitlines()[0] if result.stdout else "No HTTP Status Line"
                    print(f"  SUCCESS. {status_line}")
                else:
                    print(f"  FAILED. Curl exited with code: {result.returncode}")
                    if result.stderr:
                        print(f"  Stderr: {result.stderr.strip()}")
                    if result.stdout:
                        print(f"  Stdout (headers): {result.stdout.strip()}")
                print("-" * 50)

            except FileNotFoundError:
                print(f"Error: 'curl' command not found. Please ensure curl is installed and in your system's PATH.")
                break
            except Exception as e:
                print(f"An unexpected error occurred while executing curl for '{url}': {e}")
                print("-" * 50)

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it exists.")
    except Exception as e:
        print(f"An error occurred while reading '{file_path}': {e}")

if __name__ == "__main__":
    print('\nStarting Manual Daddy script...\n')
    
    # Prompt for the specific ID
    try:
        premium_id = input("Enter the ID of the channel giving a 403/418: ").strip()
        if not premium_id:
            print("No ID entered. Exiting.")
            exit(1)
        premium_id = int(premium_id)  # Convert to int for validation
    except ValueError:
        print("Invalid ID entered. Must be a number. Exiting.")
        exit(1)
    
    # Step 1: Fetch and decode data for the specific ID
    print(f'\nFetching data for ID {premium_id}...')
    success = get_and_decode_data_for_id(premium_id, CHANNEL_AUTH_FILE)
    if not success:
        print("Failed to fetch or decode data. Exiting.")
        exit(1)
    print('Channel data fetching completed.\n')
    
    # Step 2: Generate auth URLs
    print('Generating auth.php URLs...')
    generated_urls = generate_auth_urls_from_channel_auth_file(CHANNEL_AUTH_FILE)
    
    if generated_urls:
        try:
            with open(OUTPUT_URLS_FILE, 'w') as f:
                for url in generated_urls:
                    f.write(url + '\n')
            print(f"Successfully generated {len(generated_urls)} auth.php URLs.\n")
        except IOError as e:
            print(f"Error writing to file '{OUTPUT_URLS_FILE}': {e}")
            exit(1)
    else:
        print(f"No auth.php URLs generated. Please check your '{CHANNEL_AUTH_FILE}' file's content and format.")
        exit(1)
    
    # Step 3: Execute curl commands
    execute_curl_commands_from_file(OUTPUT_URLS_FILE)
    
    print("\nManual Daddy script completed.")