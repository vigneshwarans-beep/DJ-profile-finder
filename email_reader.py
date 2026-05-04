import imaplib
import email
import os
from email.header import decode_header

# --- CONFIGURATION ---
# Note: For Gmail, you MUST use an "App Password" if 2FA is enabled.
# You cannot use your normal account password.
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
DOWNLOAD_FOLDER = "candidate_documents"

def create_download_folder():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

def decode_str(header_str):
    """Helper function to decode email headers"""
    decoded_parts = decode_header(header_str)
    result = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="ignore")
        else:
            result += part
    return result

def check_for_candidate_emails():
    """
    Connects to the email server, searches for new candidate emails,
    and downloads their attached documents (Resumes, Passports).
    """
    create_download_folder()
    
    try:
        print(f"Connecting to {IMAP_SERVER}...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        
        # Select the inbox
        mail.select("inbox")
        
        # Search for all UNREAD emails. 
        # You could also search by subject: '(UNREAD SUBJECT "Application")'
        status, messages = mail.search(None, 'UNREAD')
        
        if status != "OK":
            print("No new messages found or error searching.")
            return

        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} new unread emails.")

        for email_id in email_ids:
            # Fetch the email data (RFC822 is the standard format)
            res, msg_data = mail.fetch(email_id, '(RFC822)')
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse the raw email bytes
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject = decode_str(msg.get("Subject", ""))
                    sender = decode_str(msg.get("From", ""))
                    print(f"\nProcessing Email from: {sender}")
                    print(f"Subject: {subject}")
                    
                    # Iterate over email parts to find attachments
                    if msg.is_multipart():
                        for part in msg.walk():
                            # Skip multipart containers
                            if part.get_content_maintype() == 'multipart':
                                continue
                            # Skip parts that don't have a filename (usually text/html bodies)
                            filename = part.get_filename()
                            if not filename:
                                continue
                                
                            filename = decode_str(filename)
                            
                            # We only want images and PDFs for now
                            if filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                                filepath = os.path.join(DOWNLOAD_FOLDER, filename)
                                
                                # Save the attachment
                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                print(f"✅ Downloaded attachment: {filename}")
                                
                    else:
                        print("Email is not multipart (no attachments).")
                        
            # Mark the email as Read (optional, but good for testing so it doesn't loop forever)
            # mail.store(email_id, '+FLAGS', '\Seen')

        mail.close()
        mail.logout()
        print("\nFinished checking emails.")
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch emails: {e}")
        print("Tip: If using Gmail, ensure you created an 'App Password' instead of your regular password.")

if __name__ == "__main__":
    check_for_candidate_emails()
