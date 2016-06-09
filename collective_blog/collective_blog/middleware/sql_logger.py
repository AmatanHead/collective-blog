"""Middleware that prints all database queries

Use for fast database inspections.
Taken from https://djangosnippets.org/snippets/264/

"""

from django.db import connection


class TerminalLoggingMiddleware:
    @staticmethod
    def process_response(request, response):
        """Reads the query data and prints it"""
        from sys import stdout
        if stdout.isatty():
            for query in connection.queries:
                print("\033[1;31m[%s]\033[0m \033[1m%s\033[0m" % (
                    query['time'], " ".join(query['sql'].split())))
        return response
