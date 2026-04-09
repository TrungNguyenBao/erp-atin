"""Migrate sprint state: closed → done."""


def migrate(cr, version):
    cr.execute("UPDATE project_sprint SET state = 'done' WHERE state = 'closed'")
