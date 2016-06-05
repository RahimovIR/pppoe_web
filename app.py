from collections import defaultdict

import web

import config
from marshmallow_jsonapi import Schema, fields
from pyroute2 import IPRoute
from subprocess import call
import json


VERSION = "0.0.1"

INTERFACE = "ppp0"

urls = (
    r'/', 'Index',
    r'/get_status', 'Status',
    r'/get_log', 'Log',
    r'/set_connect', 'Connect',
    r'/set_disconnect', 'Disconnect',
    )

app = web.application(urls, globals())


render = web.template.render('templates/',
                             base='base',
                             cache=config.cache)
# t_globals = web.template.Template.globals
# t_globals['datestr'] = web.datestr
# t_globals['app_version'] = lambda: VERSION + ' - ' + config.env
# t_globals['render'] = lambda t, *args: render._template(t)(*args)


class Index:
    def GET(self):
        return render.index(INTERFACE)

class Status:
    def GET(self):
        st = StatusSchema()
        web.header('Content-Type', 'application/json')
        data, errs = st.dump(st)
        return json.dumps(data)

class Log:
    def GET(self):
        log = LogSchema()
        web.header('Content-Type', 'application/json')
        data, errs = log.dump(log)
        return json.dumps(data)

class Connect:
    def GET(self):
        cr = CommandResult()
        cr.exitCode = call(["sudo", "pon", "dsl-provider"])
        web.header('Content-Type', 'application/json')
        data, errs = cr.dump(cr)
        return json.dumps(data)

class Disconnect:
    def GET(self):
        cr = CommandResult()
        cr.exitCode = call(["sudo", "poff", "dsl-provider"])
        web.header('Content-Type', 'application/json')
        data, errs = cr.dump(cr)
        return json.dumps(data)

# Set a custom internal error message
def internalerror():
    msg = """
    An internal server error occurred. Please try your request again by
    hitting back on your web browser. You can also <a href="/"> go back
     to the main page.</a>
    """
    return web.internalerror(msg)


class StatusSchema(Schema):
    id = fields.Str(dump_only=True)
    connect = fields.Boolean()
    details = fields.Str()

    def __init__(self):
        ip = IPRoute()
        pppLinksIds = ip.link_lookup(ifname=INTERFACE)
        if len(pppLinksIds) > 0:
            state = ip.get_links(pppLinksIds)[0].get_attr('IFLA_OPERSTATE')
            if state == 'UP':
                self.connect = True
                self.details = INTERFACE + " interface UP"
            else:
                self.connect = False
                self.details = INTERFACE + " exist but no UP"
            ip.close()
        else:
            self.connect = False
            self.details = INTERFACE + " interface no exist"
        super(StatusSchema, self).__init__()


    class Meta:
        type_ = 'pppoe_status'
        strict = True

class LogSchema(Schema):
    id = fields.Str(dump_only=True)
    rawLog = fields.Str()

    def __init__(self):
        self.rawLog = self.getPppoeLog()
        super(LogSchema, self).__init__()

    def getPppoeLog(self, fileName="/var/log/syslog"):
        result = ""
        with open(fileName) as infile:
            for line in infile:
                if "ppp" in line:
                    result += line
        return result
    
    
    class Meta:
        type_ = 'pppoe_log'
        strict = True

class CommandResult(Schema):
    id = fields.Str(dump_only=True)
    exitCode = fields.Int()
    stdout = fields.Str()


    class Meta:
        type_ = 'pppoe_command_status'
        strict = True

# Setup the application's error handler
app.internalerror = web.debugerror if web.config.debug else internalerror


# Adds a wsgi callable for uwsgi
application = app.wsgifunc()
if __name__ == "__main__":
    app.run()
