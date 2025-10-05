
def get_speaker_booking_notification_template(event_name, event_date, event_time, booker_name, username):
    logo_url = "https://narrapro.up.railway.app/static/images/narrapro-logo.png"
    subject = "Anda Memiliki Permintaan Booking Baru!"
    html_message = f"""
    <html>
        <body style="font-family: sans-serif;">
            <img src="{logo_url}" alt="Narrapro Logo" style="max-width: 150px; margin-bottom: 20px;">
            <p>Yth. {username},</p>
            <p>Anda telah menerima permintaan booking baru untuk sebuah event.</p>
            
            <p><b>Detail Acara:</b></p>
            <ul>
                <li>Nama Acara: {event_name}</li>
                <li>Tanggal: {event_date}</li>
                <li>Waktu: {event_time}</li>
                <li>Dipesan oleh: {booker_name}</li>
            </ul>
            
            <p>Silakan login ke akun NarraPro Anda untuk meninjau dan merespons permintaan ini.</p>
            
            <p>Hormat kami,<br>
            Tim NarraPro</p>
        </body>
    </html>
    """
    return subject, html_message
