from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Mengirim email tes untuk memeriksa apakah konfigurasi email berfungsi.'

    def handle(self, *args, **options):
        self.stdout.write("Mencoba mengirim email tes...")
        try:
            sent_count = send_mail(
                subject='Email Tes dari Narrapro',
                message='Ini adalah email tes untuk memverifikasi pengaturan email Anda.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['test@example.com'],
                fail_silently=False,
            )
            if sent_count > 0:
                self.stdout.write(self.style.SUCCESS(
                    f"Berhasil mengirim email tes dari '{settings.DEFAULT_FROM_EMAIL}' ke 'test@example.com'."
                ))
                self.stdout.write(self.style.NOTICE(
                    "Periksa dasbor Resend Anda untuk mengonfirmasi pengiriman."
                ))
            else:
                self.stdout.write(self.style.WARNING("send_mail mengembalikan 0, yang berarti tidak ada email yang terkirim."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Terjadi kesalahan saat mengirim email: {e}"))
            self.stderr.write(self.style.ERROR(
                "Silakan periksa pengaturan ANYMAIL dan variabel lingkungan RESEND_API_KEY di file .env Anda."
            ))
