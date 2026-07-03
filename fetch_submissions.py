import requests
import json
import os
from datetime import datetime
import time
import html

# Your Codeforces handle
HANDLE = "nullptrx"

# Number of recent submissions to check
COUNT = 10

# Codeforces API URLs
SUBMISSION_API = f"https://codeforces.com/api/user.status?handle={HANDLE}&from=1&count={COUNT}"

def fetch_with_retry(url, max_retries=3):
    """Fetch data from API with retry mechanism"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data["status"] == "OK":
                return data
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

def load_submission_history():
    """Load previously submitted problems"""
    history_file = "submission_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_submission_history(history):
    """Save submission history"""
    with open("submission_history.json", "w") as f:
        json.dump(history, f, indent=4)

def get_solution_code(contest_id, submission_id):
    """Get the code from a Codeforces submission"""
    try:
        url = f"https://codeforces.com/contest/{contest_id}/submission/{submission_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        content = response.text
        start_marker = '<pre id="program-source-text"'
        end_marker = '</pre>'
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            # Cloudflare block or login wall hit
            return None
            
        code_start = content.find('>', start_idx) + 1
        code_end = content.find(end_marker, code_start)
        
        if code_end > code_start:
            code = content[code_start:code_end]
            return html.unescape(code)
        return None
    except Exception as e:
        print(f"Error scraping: {e}")
        return None

def get_file_extension(lang):
    """Get the file extension based on programming language"""
    lang = lang.lower()
    if "c++" in lang or "gcc" in lang:
        return "cpp"
    elif "python" in lang:
        return "py"
    elif "java" in lang:
        return "java"
    elif "javascript" in lang or "js" in lang:
        return "js"
    elif "go" in lang:
        return "go"
    elif "rust" in lang:
        return "rs"
    return "txt"

def main():
    os.makedirs("submissions", exist_ok=True)
    submitted_problems = load_submission_history()
    
    print(f"Fetching submissions for {HANDLE}...")
    try:
        data = fetch_with_retry(SUBMISSION_API)
        submissions = data["result"]
    except Exception as e:
        print(f"Failed to fetch submissions: {e}")
        return
    
    new_count = 0
    for submission in submissions:
        if submission["verdict"] != "OK":
            continue
            
        contest_id = submission["contestId"] 
        problem_index = submission["problem"]["index"]
        submission_id = submission["id"]
        problem_id = f"{contest_id}_{problem_index}"
        problem_name = submission["problem"].get("name", "Unknown")
        lang = submission["programmingLanguage"]
        extension = get_file_extension(lang)
        
        if problem_id in submitted_problems:
            continue
            
        print(f"Attempting to scrape source code for {problem_id}...")
        code = get_solution_code(contest_id, submission_id)
        
        file_path = f"submissions/{problem_id}.{extension}"
        
        if code:
            # Successfully scraped the real source code
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(code)
            print(f"Successfully archived source code for {problem_id}!")
        else:
            # Scraper blocked by Cloudflare -> Create professional metadata reference card
            submission_url = f"https://codeforces.com/contest/{contest_id}/submission/{submission_id}"
            fallback_content = (
                f"// Codeforces Problem: {problem_id} - {problem_name}\n"
                f"// Submission ID: {submission_id}\n"
                f"// Language: {lang}\n"
                f"// Status: Accepted (AC)\n"
                f"// Direct Link: {submission_url}\n\n"
                f"/* Source code scraping was restricted by provider security controls. "
                f"Access via the link above. */\n"
            )
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(fallback_content)
            print(f"Provider restriction met. Generated fallback reference card for {problem_id}.")
        
        # Log entry
        with open("submissions/log.txt", "a") as log:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"{problem_id} - {problem_name} - Solved on {timestamp}\n")
        
        submitted_problems.append(problem_id)
        new_count += 1
        time.sleep(2) # Modest sleep delay
    
    save_submission_history(submitted_problems)
    print(f"Successfully processed {new_count} new accepted solutions.")

if __name__ == "__main__":
    main()