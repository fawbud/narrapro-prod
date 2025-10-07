# Merge migration to resolve branch from 0004

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('narasumber', '0005_add_pekerjaan_jabatan'),
        ('narasumber', '0006_alter_narasumberprofile_profile_picture'),
    ]

    operations = [
        # No operations needed, just merging the branches
    ]
