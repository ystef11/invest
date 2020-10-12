#!/usr/bin/python
# coding=utf8

import argparse
import json
import sys
import twisted.web.resource
import twisted.web.server
from twisted.internet import reactor
from twisted.internet.threads import deferToThread
import invest_db
import os
import tokens
import hashlib

class web_intercom(twisted.web.resource.Resource):
    def __init__(self):
        self.debug = False
        self.html = False

    def responseFailed(self, err, request):
        pass
        request.setResponseCode(401)
        request.write(json.dumps({'code': -100, 'message': 'responseFailed'}))
        request.finish()

    def render_GET(self, request):
        # for i in request.args:
        #    print 'arg:', i, '=', request.args[i][0]
        print request.getClientIP(), request.getHeader('x-real-ip'), '>', request.args
        deferToThread(self.init, request).addCallback(self.writeResponse, request).addErrback(self.onError, request)
        return twisted.web.server.NOT_DONE_YET

    def render_POST(self, request):
        body = request.content.getvalue()
        # print body
        try:
            js = json.loads(body)
            for i in js:
                request.args[i] = [js[i]]
        except:
            print 'exception json.loads(body)'
            pass
        # for i in request.args:
        print request.getClientIP(), request.getHeader('x-real-ip'), '>', request.args
        deferToThread(self.init, request).addCallback(self.writeResponse, request).addErrback(self.onError, request)
        return twisted.web.server.NOT_DONE_YET

    def ctoken(self, request):
        s_ip = request.getClientIP()
        # print 'x-forwarded-for',request.getHeader('x-forwarded-for')
        cip = request.getHeader('x-real-ip')
        # return
        if 'pwd' in request.args and 'user' in request.args:
            pwd = request.args['pwd'][0]
            user = request.args['user'][0]
            if user not in tokens.pwd:
                raise Exception('bad user')
            t = hashlib.sha256(tokens.pwd[user])
            # dt += datetime.timedelta(minutes=13)
            if pwd != t.hexdigest():
                raise Exception('bad pwd')
        else:
            raise Exception('no pwd')

    def init(self, request):
        #            print request.getHeader('Content-type')
        self.ctoken(request)
        cip = request.getHeader('x-real-ip')
        args = ''
        if 'action' in request.args:
            s = request.args['action'][0]
            s = s.replace('"', '').replace("'", '')
            db = invest_db.DB()
            if s not in dir(db):
                raise Exception('error function')
            args_f = eval('db.%s.__code__.co_varnames' % s)
            args += self.get_eval_args(args_f, request.args)
            try:
                ex = 'db.%s(%s)' % (s, args)
                print cip, 'execute:', ex
                ret = eval(ex)
                db.close()
                return {'code': 0, 'result': ret}
            except Exception as ex:
                print 'Exception eval(ex)'
                raise Exception(ex)
        else:
            raise Exception('no arguments')

    def get_eval_args(self, params, r_args, exclude = []):
        args = ''
        for i in params:
            if i == 'self': continue
            if i in exclude: continue
            if i in r_args:
                if type(r_args[i][0]) == str or type(r_args[i][0]) == unicode:
                    args += '%s="%s",' % (i, r_args[i][0])
                else:
                    args += '%s=%s,' % (i, r_args[i][0])
        return args

    # write output to client
    def writeResponse(self, result, request):
        print request.getClientIP(), request.getHeader('x-real-ip'), '<answer', json.dumps(result, sort_keys=True,
                                                                                           default=str)
        request.setHeader('Content-type', 'text/json')
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.write(json.dumps(result, sort_keys=True, default=str))
        request.finish()

    def onError(self, err, request):
        err_trace = ''
        for i in err.frames:
            err_trace += str(i) + '|'
        if 'debug' in request.args:
            text = str(err)
        else:
            text = str(err.getErrorMessage())
        print request.getClientIP(), request.getHeader('x-real-ip'), '<error', str(err.getErrorMessage()), err_trace
        request.setHeader('Content-type', 'text/json')
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.write(json.dumps({'code': -100, 'message': str(text), 'result':[]}))
        request.finish()


if __name__ == "__main__":
    # parsing input arguments
    ip = '5.3.6.108'
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", help="IP address which is used to accept incoming HTTP requests", type=str,
                        default=ip)
    parser.add_argument("--port", help="listen port", type=int, default=7777)
    args = parser.parse_args()

    root = twisted.web.resource.Resource()
    root.putChild("invest", web_intercom())
    factory = twisted.web.server.Site(root)
    reactor.listenTCP(args.port, factory, interface=args.ip)
    reactor.run()
