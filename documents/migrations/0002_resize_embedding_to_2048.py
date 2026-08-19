from django.db import migrations


def resize_embedding_column(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    # Existing rows may contain 1536-d vectors from older runs.
    # Clear them so the type change to vector(2048) is always safe.
    schema_editor.execute(
        "UPDATE documents_documentchunk SET embedding = NULL WHERE embedding IS NOT NULL;"
    )
    schema_editor.execute(
        "ALTER TABLE documents_documentchunk "
        "ALTER COLUMN embedding TYPE vector(2048);"
    )


def noop(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(resize_embedding_column, reverse_code=noop),
    ]

