
import unittest
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model

from narrapro.email_service import (
    send_speaker_booking_notification,
    send_new_user_confirmation,
    send_booking_status_update,
    send_new_application_notification,
    send_application_status_update
)

User = get_user_model()

class EmailNotificationTests(TestCase):

    @patch('narrapro.email_service.send_mail')
    def test_send_speaker_booking_notification(self, mock_send_mail):
        send_speaker_booking_notification(
            recipient_list=['speaker@example.com'],
            event_name='Test Event',
            event_date='2025-10-26',
            event_time='10:00',
            booker_name='Test Booker'
        )
        self.assertTrue(mock_send_mail.called)
        call_args = mock_send_mail.call_args
        self.assertEqual(call_args[0][0], 'Anda Memiliki Permintaan Booking Baru!')
        self.assertIn('Test Event', call_args[0][3])
        self.assertEqual(call_args[1]['from_email'], 'from@example.com')
        self.assertEqual(call_args[1]['recipient_list'], ['speaker@example.com'])

    @patch('narrapro.email_service.send_mail')
    def test_send_new_user_confirmation(self, mock_send_mail):
        send_new_user_confirmation(
            recipient_list=['newuser@example.com'],
            username='newuser'
        )
        self.assertTrue(mock_send_mail.called)
        call_args = mock_send_mail.call_args
        self.assertEqual(call_args[0][0], 'Selamat Datang di NarraPro!')
        self.assertIn('newuser', call_args[0][3])
        self.assertEqual(call_args[1]['from_email'], 'from@example.com')
        self.assertEqual(call_args[1]['recipient_list'], ['newuser@example.com'])

    @patch('narrapro.email_service.send_mail')
    def test_send_booking_status_update(self, mock_send_mail):
        send_booking_status_update(
            recipient_list=['booker@example.com'],
            status='Accepted',
            event_name='Test Event'
        )
        self.assertTrue(mock_send_mail.called)
        call_args = mock_send_mail.call_args
        self.assertEqual(call_args[0][0], 'Update Status Booking untuk Acara Test Event')
        self.assertIn('Accepted', call_args[0][3])
        self.assertEqual(call_args[1]['from_email'], 'from@example.com')
        self.assertEqual(call_args[1]['recipient_list'], ['booker@example.com'])

    @patch('narrapro.email_service.send_mail')
    def test_send_new_application_notification(self, mock_send_mail):
        send_new_application_notification(
            recipient_list=['host@example.com'],
            applicant_name='Test Applicant',
            event_name='Test Job'
        )
        self.assertTrue(mock_send_mail.called)
        call_args = mock_send_mail.call_args
        self.assertEqual(call_args[0][0], 'Lamaran Baru untuk Acara Test Job')
        self.assertIn('Test Applicant', call_args[0][3])
        self.assertEqual(call_args[1]['from_email'], 'from@example.com')
        self.assertEqual(call_args[1]['recipient_list'], ['host@example.com'])

    @patch('narrapro.email_service.send_mail')
    def test_send_application_status_update(self, mock_send_mail):
        send_application_status_update(
            recipient_list=['applicant@example.com'],
            status='Accepted',
            event_name='Test Job'
        )
        self.assertTrue(mock_send_mail.called)
        call_args = mock_send_mail.call_args
        self.assertEqual(call_args[0][0], 'Update Status Lamaran untuk Acara Test Job')
        self.assertIn('Accepted', call_args[0][3])
        self.assertEqual(call_args[1]['from_email'], 'from@example.com')
        self.assertEqual(call_args[1]['recipient_list'], ['applicant@example.com'])
