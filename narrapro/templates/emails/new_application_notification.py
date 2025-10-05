
def get_new_application_notification_template(applicant_name, event_name):
    logo_url = "https://narrapro.up.railway.app/static/images/narrapro-logo.png"
    subject = f"Lamaran Baru untuk Acara {event_name}"
    html_message = f"""
    <html>
        <body style="font-family: sans-serif;">
            <img src="{logo_url}" alt="Narrapro Logo" style="max-width: 150px; margin-bottom: 20px;">
            <p>Yth. Penyelenggara Acara,</p>
            <p>Anda telah menerima lamaran baru untuk acara <b>{event_name}</b>.</p>
            <p>Nama Pelamar: <b>{applicant_name}</b></p>
            
            <p>Silakan login ke akun NarraPro Anda untuk meninjau lamaran ini.</p>
            
            <p>Hormat kami,<br>
            Tim NarraPro</p>
        </body>
    </html>
    """
    return subject, html_message
