from django.core.management import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.recorder import MigrationRecorder
from django.db.models import QuerySet

FORMAT_CSV = 'csv'
FORMAT_CONSOLE = 'console'


class Command(BaseCommand):
    """
    Displays all the migration records (from the ``django_migrations`` table).
    """

    @staticmethod
    def _format_csv(record: MigrationRecorder.Migration) -> str:
        return f"{record.id},{record.applied.isoformat()},{record.app},{record.name}"

    @staticmethod
    def _format_console(record: MigrationRecorder.Migration, app_name_width: int) -> str:
        return (
            f"{str(record.id).rjust(6, ' ')} {record.applied.isoformat()} "
            f"{record.app.rjust(app_name_width, ' ')} {record.name}"
        )

    @staticmethod
    def _format_header_console(app_name_width: int) -> str:
        return (
            f"{'ID'.rjust(6, ' ')} {'Applied'.ljust(32, ' ')} "
            f"{'App'.ljust(app_name_width, ' ')} Name"
        )

    @staticmethod
    def _find_max_app_name_width(migration_query_set: QuerySet) -> int:
        return max(*[len(m['app']) for m in migration_query_set.values('app').distinct()])

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            default=FORMAT_CONSOLE,
            help=f'The format to display the migration records (csv or console). Default is: "{FORMAT_CONSOLE}"'
        )

    def handle(self, *args, **options):
        print_format = options['format']

        connection = connections[DEFAULT_DB_ALIAS]
        connection.prepare_database()
        recorder = MigrationRecorder(connection)
        migrations_queryset = recorder.migration_qs.all()

        app_name_width = 0
        header = "ID,Applied,App,Name"
        if print_format == FORMAT_CONSOLE:
            app_name_width = max(self._find_max_app_name_width(migrations_queryset), 5)
            header = self._format_header_console(app_name_width)

        print(header)
        for record in migrations_queryset:
            if print_format == FORMAT_CSV:
                row = self._format_csv(record)
            else:
                row = self._format_console(record, app_name_width)
            print(row)