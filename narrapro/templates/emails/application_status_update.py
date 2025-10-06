
def get_application_status_update_template(status, event_name, username):
    logo_url = "https://narrapro.up.railway.app/static/images/narrapro-logo.png"
    subject = f"Update Status Lamaran untuk Acara {event_name}"
    html_message = f"""
    <html>
        <body style="font-family: sans-serif;">
            <img src="{logo_url}" alt="Narrapro Logo" style="max-width: 150px; margin-bottom: 20px;">
            <p>Yth. {username},</p>
            <p>Status lamaran Anda untuk acara <b>{event_name}</b> telah diperbarui.</p>
            <p>Status baru: <b>{status}</b></p>
            
            <p>Terima kasih atas partisipasi Anda.</p>
            
            <p>Hormat kami,<br>
            Tim NarraPro</p>
        </body>
    </html>
    """
    return subject, html_message
