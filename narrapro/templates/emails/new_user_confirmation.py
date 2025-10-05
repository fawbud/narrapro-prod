
def get_new_user_confirmation_template(username):
    logo_url = "https://narrapro.up.railway.app/static/images/narrapro-logo.png"
    subject = "Selamat Datang di NarraPro!"
    html_message = f"""
    <html>
        <body style="font-family: sans-serif;">
            <img src="{logo_url}" alt="Narrapro Logo" style="max-width: 150px; margin-bottom: 20px;">
            <p>Yth. {username},</p>
            <p>Terima kasih telah mendaftar di NarraPro. Akun Anda telah berhasil dibuat.</p>
            <p>Anda sekarang dapat login dan mulai menjelajahi fitur-fitur kami.</p>
            
            <p>Selamat datang di komunitas kami!</p>
            
            <p>Hormat kami,<br>
            Tim NarraPro</p>
        </body>
    </html>
    """
    return subject, html_message
