import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from flask import Flask, request, jsonify, render_template, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL = os.environ.get("SENDER_EMAIL", "premiumsubsciptionbd@gmail.com") 
PASSWORD = os.environ.get("SENDER_PASSWORD", "ooew ksav ygtf lntl")

def send_email(to_email, subject, html_content, from_name="Google", from_email=None):
    sender_email = EMAIL
    sender_password = PASSWORD

    if not sender_email or not sender_password:
        raise ValueError("Server email configuration is missing (SENDER_EMAIL or SENDER_PASSWORD).")
        
    if not from_email:
        from_email = sender_email

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = formataddr((from_name, from_email))
    msg['To'] = to_email
    
    plain_text = f"Hello,\n\n{subject}\n\nThanks,\n{from_name}"
    msg.set_content(plain_text)
    msg.add_alternative(html_content, subtype='html')

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/send', methods=['POST'])
def handle_send():
    data = request.json
    
    to_email = data.get('to_email')
    template_type = data.get('template_type') # youtube, storage, combo
    lang = data.get('lang') # bn, en
    
    sender_name = data.get('sender_name')
    if not sender_name:
        sender_name = "YouTube Premium" if template_type == "youtube" else "Premium Wala"
        
    sender_email = data.get('sender_email', 'noreply@premiumwala.com')
    
    receiver_name = data.get('receiver_name')
    if not receiver_name or str(receiver_name).strip() == '':
        receiver_name = to_email.split('@')[0].replace('.', ' ').title()
        
    receiver_email = data.get('receiver_email', to_email)
    invite_link = data.get('invite_link', '#')
    
    if not to_email or not template_type or not lang or not invite_link:
        return jsonify({"error": "Missing required fields"}), 400
        
    template_name = f"{template_type}_{lang}.html"
    
    try:
        template_path = os.path.join(app.root_path, 'templates', 'emails', template_name)
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        subject = ""
        if template_type == "youtube":
            subject = f"আপনাকে YouTube Premium-এ আমন্ত্রণ জানানো হয়েছে" if lang == 'bn' else f"You're invited to YouTube Premium"
        elif template_type == "storage":
            subject = f"আপনার Google One স্টোরেজ আমন্ত্রণ" if lang == 'bn' else f"Your Google One storage invitation"
        elif template_type == "combo":
            subject = f"YouTube Premium এবং Google One স্টোরেজ আমন্ত্রণ" if lang == 'bn' else f"YouTube Premium and Google One storage invitation"
            
        html_content = render_template_string(
            template_content, 
            sender_name=sender_name, 
            sender_email=sender_email,
            receiver_name=receiver_name,
            receiver_email=receiver_email,
            invite_link=invite_link
        )
        
        from_display_name = sender_name
             
        send_email(to_email, subject, html_content, from_name=from_display_name, from_email=EMAIL)
        
        return jsonify({"success": True, "message": "Email sent successfully!"})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
