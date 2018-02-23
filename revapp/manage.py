from . import create_app, app, db
from flask_script import Manager, Server, prompt_bool
from flask_migrate import Migrate, MigrateCommand
from flask import url_for
import models

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def create():
    print 'Initializing the db'
    "create the database"
    db.create_all()

@manager.command
def drop():
    print 'Dropping the db'
    "drop the database"
    if prompt_bool(
        "Are you sure you want to lose all your data"):
        db.drop_all()
        try:
            db.session.execute("DROP TABLE alembic_version")
            db.session.commit()
        except:
            pass

@manager.command
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        methods = ','.join(rule.methods)
        # url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)
    for line in sorted(output):
        print line


if __name__ == "__main__":
    create_app()
    manager.run()