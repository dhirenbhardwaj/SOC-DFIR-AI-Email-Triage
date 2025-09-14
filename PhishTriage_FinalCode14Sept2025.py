import os
import email
from email import policy
import json, base64
import google.generativeai as genai


# Configure the API key from an environment variable
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def read_eml_files(folder_path):
    all_emails_data = []  # collect everything to also write JSON later

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".eml"):
            continue

        file_path = os.path.join(folder_path, filename)
        with open(file_path, "rb") as f:
            msg = email.message_from_binary_file(f, policy=policy.default)

        # ------- print section (your original behavior) -------
        print("=" * 80)
        print(f"File: {filename}")

        print("\n--- Headers ---")
        for header, value in msg.items():
            print(f"{header}: {value}")

        print("\n--- Body ---")

        # ------- build a JSON-friendly record in parallel -------
        email_info = {
            "filename": filename,
            "headers": {k: v for k, v in msg.items()},
            "body_text": "",
            "body_html": "",
            "attachments": []  # [{filename, content_type, size_bytes, content_base64}]
        }

        if msg.is_multipart():
            for part in msg.walk():
                if part.is_multipart():
                    continue
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition") or "")

                # Body text
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body_text = part.get_content()
                    except Exception:
                        payload = part.get_payload(decode=True) or b""
                        body_text = payload.decode("utf-8", errors="replace")
                    print(body_text)
                    email_info["body_text"] += body_text

                # Body HTML
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        body_html = part.get_content()
                    except Exception:
                        payload = part.get_payload(decode=True) or b""
                        body_html = payload.decode("utf-8", errors="replace")
                    print("\n[HTML Version Below]\n")
                    print(body_html)
                    email_info["body_html"] += body_html

                # Attachments
                elif "attachment" in content_disposition:
                    fname = part.get_filename() or "Unnamed_Attachment"
                    payload = part.get_payload(decode=True) or b""

                    print(f"\n--- Attachment: {fname} ---")
                    if payload:
                        try:
                            # try show as UTF-8 text
                            print(payload.decode("utf-8", errors="ignore"))
                        except Exception:
                            print(repr(payload))

                    # also store in JSON (base64 so JSON can carry bytes)
                    email_info["attachments"].append({
                        "filename": fname,
                        "content_type": content_type,
                        "size_bytes": len(payload),
                        "content_base64": base64.b64encode(payload).decode("ascii")
                    })
        else:
            # Single-part email
            try:
                body_text = msg.get_content()
            except Exception:
                payload = msg.get_payload(decode=True) or b""
                body_text = payload.decode("utf-8", errors="replace")
            print(body_text)
            email_info["body_text"] = body_text

        # add this email’s info to the big list
        all_emails_data.append(email_info)

    # return everything so caller can write JSON
    return all_emails_data


def load_plugin_output(output_filename):
    with open(output_filename, 'r', encoding = "utf-8") as file:
        emails = json.load(file)
        return emails



def ask_gemini(prompt_text: str) -> str:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt_text)
    return response.text
  

# ===== main (kept your variables) =====
folder = r"C:\Users\dhire\Documents\phishing_pot\phishing_pot-main\test"
extracted = read_eml_files(folder)  # still prints

# also write one JSON file with bodies + attachments
output_filename = r"C:\Users\dhire\Documents\phishing_pot\phishing_pot-main\test\eml_data_output.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(extracted, f, ensure_ascii=False, indent=2)

file_output = load_plugin_output(output_filename)

print(f"\n[JSON] Successfully saved email data to {output_filename}")

 # Create a question for GPT
prompt = f"""
You are a cybersecurity expert. Analyze the following JSON data extracted from an email
and determine if it is a phishing attempt. Provide a detailed,
step-by-step analysis that includes:

1. Sender Analysis: Scrutinize the 'From' and 'Return-Path' headers. Comment on legitimacy.
2. Authentication Results: Review 'Authentication-Results' for SPF/DKIM/DMARC and explain fails/none.
3. Content and Urgency: Look for social engineering tactics in subject/body.
4. Link Analysis: Note any URLs and mismatches between visible text and destination.
5. Final Verdict: "This is a phishing email" or "This is a legitimate email", with key findings.

"""
payload = json.dumps(file_output, ensure_ascii=False,indent=2)


full_prompt = prompt + "\nINPUT_EMAILS_JSON:\n" + payload

Summary = ask_gemini(full_prompt)

print(Summary)
