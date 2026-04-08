from django.core.management.base import BaseCommand

from app.services import ensure_sqlite_decimal_storage_integrity


class Command(BaseCommand):
    help = "Repair malformed DecimalField values stored in SQLite."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            default=None,
            help="Restrict the repair pass to a single user_id when the table has a user column.",
        )

    def handle(self, *args, **options):
        result = ensure_sqlite_decimal_storage_integrity(user_id=options["user_id"])
        self.stdout.write(
            self.style.SUCCESS(
                f"SQLite decimal repair complete: {result['updated_rows']} row updates across {result['updated_fields']} field scans."
            )
        )
