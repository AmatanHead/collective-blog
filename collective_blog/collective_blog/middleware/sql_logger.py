from django.db import connection


# From https://djangosnippets.org/snippets/264/
class TerminalLogging:
    @staticmethod
    def process_response(request, response):
        from sys import stdout
        if stdout.isatty():
            for query in connection.queries:
                print("\033[1;31m[%s]\033[0m \033[1m%s\033[0m" % (
                    query['time'], " ".join(query['sql'].split())))
        return response
