import requests
from flask import render_template
from common.cli.celery_cli import celery_cli
from common.cli.db_cli import db_cli
from common.cli.task_cli import task_cli
from common.cli.ansible_cli import ansible_cli
from common.cli.webssh_cli import webssh_cli
from api.view import *

app.cli.add_command(task_cli)
app.cli.add_command(celery_cli)
app.cli.add_command(db_cli)
app.cli.add_command(ansible_cli)
app.cli.add_command(webssh_cli)


@app.route('/')
def hello_world():
    return 'Welcome to use AutoOps-2.0!'


@app.route('/connect')
def ssh_connect():
    host = request.args.get('host', '192.168.1.100')
    data = {
        'hostname': host,
        'port': 2222,
        'username': 'zhxia',
        'term': 'xterm-256color',
    }
    files = {'privatekey': open('/Users/zhxia/id_rsa', 'rb')}

    print files
    resp = requests.post('http://localhost:8888', data, files=files)
    json_data = resp.json()
    # print json_data
    return render_template('terminator.html', **json_data)


if __name__ == '__main__':
    app.run()
