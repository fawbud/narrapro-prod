# Generated migration for adding pekerjaan and jabatan fields

from django.db import migrations, models


def set_default_values(apps, schema_editor):
    """Set default values for existing narasumber profiles"""
    NarasumberProfile = apps.get_model('narasumber', 'NarasumberProfile')
    NarasumberProfile.objects.filter(pekerjaan__isnull=True).update(pekerjaan='Karyawan')
    NarasumberProfile.objects.filter(jabatan__isnull=True).update(jabatan='Manajer')


class Migration(migrations.Migration):

    dependencies = [
        ('narasumber', '0004_alter_narasumberprofile_profile_picture'),
    ]

    operations = [
        # Add fields as nullable first
        migrations.AddField(
            model_name='narasumberprofile',
            name='pekerjaan',
            field=models.CharField(blank=True, null=True, max_length=40, help_text='Occupation/job of the narasumber'),
        ),
        migrations.AddField(
            model_name='narasumberprofile',
            name='jabatan',
            field=models.CharField(blank=True, null=True, max_length=40, help_text='Position/title of the narasumber'),
        ),
        # Set default values for existing records
        migrations.RunPython(set_default_values, reverse_code=migrations.RunPython.noop),
        # Make fields non-nullable
        migrations.AlterField(
            model_name='narasumberprofile',
            name='pekerjaan',
            field=models.CharField(max_length=40, help_text='Occupation/job of the narasumber'),
        ),
        migrations.AlterField(
            model_name='narasumberprofile',
            name='jabatan',
            field=models.CharField(max_length=40, help_text='Position/title of the narasumber'),
        ),
    ]
