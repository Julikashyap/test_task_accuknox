from django.db import migrations
from django.contrib.auth.models import Group, Permission


def create_superusers(apps, schema_editor):
    User = apps.get_model('tes_app', 'User')
    User.objects.create_superuser(
        username='superuser@gmail.com', 
        first_name="Super", 
        last_name="User", 
        name="Juli",
        email='superuser@gmail.com', 
        password='Admin@1234'
    )
    User.objects.create_superuser(
        username='juhi@gmail.com', 
        first_name="Juhi", 
        last_name="Kashyap", 
        name="Test",
        email='juhi@gmail.com', 
        password='Admin@1234'
    )


def create_groups(apps, schema_editor):
    # Get the Group and Permission models
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Create the groups
    admin_group, _ = Group.objects.get_or_create(name='admin')
    write_group, _ = Group.objects.get_or_create(name='write')
    read_group, _ = Group.objects.get_or_create(name='read')

    # Assign permissions to groups
    # Admin has all permissions
    all_permissions = Permission.objects.all()
    admin_group.permissions.set(all_permissions)

    # Write group permissions (get and post)
    write_permissions = Permission.objects.filter(
        codename__in=['add_modelname', 'change_modelname', 'view_modelname']
    )  # Replace 'modelname' with the model(s) you want to give permissions for
    write_group.permissions.set(write_permissions)

    # Read group permissions (only get)
    read_permissions = Permission.objects.filter(codename__in=['view_modelname'])
    read_group.permissions.set(read_permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('tes_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superusers),
        migrations.RunPython(create_groups),
    ]
