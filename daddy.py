import requests
import re
import base64
import subprocess
import os

# --- Configuration ---
INPUT_FILES = ["ddy6.dat", "nfs.dat", "wind.dat", "zeko.dat", "dokko1.dat"]
CHANNEL_AUTH_FILE = "keys.dat"
OUTPUT_URLS_FILE = "urls.dat"

def load_premium_numbers(filenames):
    """
    Loads premium numbers from the provided text files by extracting the numeric portion
    of 'premiumXXX/' entries.
    """
    premium_numbers = set()  # Use a set to avoid duplicates
    for filename in filenames:
        try:
            with open(filename, 'r') as f:
                content = f.read()
                # Extract numbers from 'premiumXXX/' patterns
                matches = re.findall(r'premium(\d+)/', content)
                premium_numbers.update(matches)
        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    return sorted([int(num) for num in premium_numbers])  # Convert to integers and sort

def get_and_decode_data(premium_numbers, output_file="keys.dat"):
    """
    Fetches data from a URL for each premium number, extracts a base64 string, and decodes
    specific nested base64 values within it. It also extracts the CHANNEL_KEY, and
    writes all output to a specified file.
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "referer": "https://daddylivestream.com"
    }

    with open(output_file, 'w') as f:
        for premium_id in premium_numbers:
            url = f"https://jxoxkplay.xyz/premiumtv/daddylivehd.php?id={premium_id}"
            f.write(f"\nProcessing ID: {premium_id}\n")
            f.write("=" * 50 + "\n")
            
            try:
                # 1. Fetch the webpage content
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an HTTPError for bad responses

                # 2. Extract the CHANNEL_KEY and write to file
                channel_key_match = re.search(r'CHANNEL_KEY="(premium[0-9]+)"', response.text)
                if channel_key_match:
                    f.write(f"CHANNEL_KEY: {channel_key_match.group(1)}\n")
                else:
                    f.write("CHANNEL_KEY: Not found\n")

                # 3. Extract the main 292-character base64 string
                main_base64_match = re.search(r'"([A-Za-z0-9+/=]{292})"', response.text, re.DOTALL)

                if not main_base64_match:
                    f.write("Error: 292-character base64 string not found.\n")
                    continue

                main_base64_string = main_base64_match.group(1)

                # 4. Decode the main base64 string
                try:
                    decoded_content = base64.b64decode(main_base64_string).decode('utf-8')
                except base64.binascii.Error as e:
                    f.write(f"Error decoding the main base64 string: {e}\n")
                    continue
                
                # 5. Find the nested base64 values
                b_ts_match = re.search(r'"b_ts":"([A-Za-z0-9+/=]+)"', decoded_content)
                b_rnd_match = re.search(r'"b_rnd":"([A-Za-z0-9+/=]+)"', decoded_content)
                b_sig_match = re.search(r'"b_sig":"([A-Za-z0-9+/=]+)"', decoded_content)

                # 6. Write the results to the file
                if b_ts_match:
                    f.write(f"b_ts: {b_ts_match.group(1)}\n")
                else:
                    f.write("b_ts: Not found\n")

                if b_rnd_match:
                    f.write(f"b_rnd: {b_rnd_match.group(1)}\n")
                else:
                    f.write("b_rnd: Not found\n")

                if b_sig_match:
                    f.write(f"b_sig: {b_sig_match.group(1)}\n")
                else:
                    f.write("b_sig: Not found\n")

            except requests.exceptions.RequestException as e:
                f.write(f"Error during the web request for ID {premium_id}: {e}\n")

def generate_auth_urls_from_channel_auth_file(file_path):
    """
    Reads keys.dat, extracts authentication parameters,
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
                    if status_line == "HTTP/2 403":
                        print(f" FAILED. {status_line}")
                    else:
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
    print('\nStarting Daddy script...\n')
    
    # Step 1: Fetch and decode data
    print('Scraping channel data... This is going to take a while.')
    premium_numbers = load_premium_numbers(INPUT_FILES)
    get_and_decode_data(premium_numbers, CHANNEL_AUTH_FILE)
    print('Channel data scraping completed.\n')
    
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
            generated_urls = []
    else:
        print(f"No auth.php URLs generated. Please check your '{CHANNEL_AUTH_FILE}' file's content and format.")
    
    # Step 3: Execute curl commands
    if generated_urls:
        execute_curl_commands_from_file(OUTPUT_URLS_FILE)
    
    print("\nDaddy script completed.")
