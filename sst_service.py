#!/usr/bin/env python3


"""
"""
import time
import glob
import pathlib
import logging
import secrets
import shutil
import os

import xmlschema
import xmlschema.extras.wsdl

import xml.etree

import tornado.ioloop
import tornado.web

from config import ROOT, DEBUG, config


class SoapEnvelope:
    """ 
    """

    ENVELOPE_URL = 'http://schemas.xmlsoap.org/soap/envelope/'
    SCHEMA_URL = 'http://www.w3.org/2001/XMLSchema-instance'

    def add_env_ns(self, name):
        return '{' + SoapEnvelope.ENVELOPE_URL + '}' + name

    def add_sche_ns(self, name):
        return '{' + SoapEnvelope.ENVELOPE_URL + '}' + name

    def __init__(self):
        
        
        self.envelope = xml.etree.ElementTree.Element('soapenv:Envelope')
        self.envelope.set('xmlns:soapenv', SoapEnvelope.ENVELOPE_URL)
        self.envelope.set('xmlns:xsi', SoapEnvelope.SCHEMA_URL)
        self.envelope.set('xsi:schemaLocation',f'{SoapEnvelope.ENVELOPE_URL} {SoapEnvelope.ENVELOPE_URL}')
        self.header = xml.etree.ElementTree.SubElement(self.envelope, 'soapenv:Header')
        self.body = xml.etree.ElementTree.SubElement(self.envelope, 'soapenv:Body')

    def get_xml(self):
        return xml.etree.ElementTree.tostring(self.envelope)

    def add_header(self, xml):
        self.header.append(xml)

    def add_body(self, xml):
        self.body.append(xml)


class WsdlService:

    def __init__(self, wsdl):
        self.wsdl = xmlschema.extras.wsdl.Wsdl11Document(wsdl)
        self.load_operations()
        self.load_actions()


    def load_operations(self):
        self.operations = {}

        for srv_name, srv in self.wsdl.services.items():
            logging.debug(f'Service: {srv.name}')

            for port_name, port in srv.ports.items():
                logging.debug(f' - Port: {port.name}')

                for op_names, op in port.binding.operations.items():
                    logging.debug(f' -- Operation: {op.name}')
                    self.operations[op.name] = op


    def load_actions(self):
        self.actions = {}
        for name, op in self.operations.items():
            if hasattr(self, op.local_name):
                self.actions[name] = getattr(self, op.local_name)
            else:
                self.actions[name] = None


    def get_input(self, xml_data):
        inputs = {}

        for name, operation in self.operations.items():
            datas = None

            for part_name, part in operation.input.message.parts.items():

                logging.debug(f' --- Parsing Input part: {part.name}')
                ns_prefix = '{' + part.target_namespace + '}'

                results = xml_data.findall(f'.//{ns_prefix}{part_name}')

                if len(results) > 0:
                    if datas is None:
                        datas = {}
                    datas[part.name] = []
                else:
                    continue

                for result in results:
                    datas[part.name] += [part.decode(result)]
            
            if datas is not None:
                inputs[name] = datas

        return inputs


    def get_output(self, datas):
        outputs = {}
        for name, data in datas.items():
            operation = self.operations[name]
            returns = []
            for part_name, part in operation.output.message.parts.items():
                logging.debug(f' --- Encoding Output part: {part.name}')

                ns_prefix = '{' + part.target_namespace + '}'
                returns += [part.encode(data)]

            outputs[name] = returns
        return outputs

    def __call__(self, xml_data):
        inputs = self.get_input(xml_data)
        
        datas = {}
        for key in inputs:
            func = self.actions[key]
            if func is not None:
                datas[key] = func(inputs[key])
        
        outputs = self.get_output(datas)
        
        return outputs

    def say_hello(self, data):
        _ns = '{spyne.examples.hello.soap}'
        d = data[f'{_ns}say_hello'][0]
        ret = {
            f'{_ns}say_helloResult': {f'{_ns}string': [d[f'{_ns}name']]*d[f'{_ns}times']},
        }

        return ret



class IndexHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ('GET','POST')

    def set_default_headers(self):
        self.set_header('Content-type', 'text/xml; charset=utf-8')


    def get(self, schema_file, *args, **kwargs):
        if schema_file.endswith('.wsdl') or schema_file.endswith('.xsd'):
            if (ROOT / 'templates' / schema_file).is_file():
                self.render(schema_file)
            else:
                self.write('<nope></nope>')
        else:
            self.write('<nope></nope>')


    def post(self, schema_file, *args, **kwargs):
        _path = pathlib.Path('./templates')
        schema_file = _path / (schema_file + '.wsdl')

        logging.info(f'Handling request from {self.request.remote_ip}')

        service = WsdlService(str(schema_file))

        xml_str = self.request.body.decode()
        envelope = SoapEnvelope()
        xml_root = xml.etree.ElementTree.XML(xml_str)

        outputs = service(xml_root)

        for key in outputs:
            for out in outputs[key]:
                envelope.add_body(out)

        soap_response = envelope.get_xml()
        self.write(soap_response)
        

def main():
    cookie_secret = secrets.token_hex()

    handlers = [(r'/(.*)', IndexHandler, {})]

    app = tornado.web.Application(
        handlers=handlers,
        template_path=ROOT / 'templates',
        static_url_prefix=f'/static/',
        static_path=ROOT / 'static',
        xsrf_cookies=False,
        debug=DEBUG,
        cookie_secret=cookie_secret,
    )

    app.listen(
        config.getint('SST Server', 'port'), 
        config.get('SST Server', 'host'),
    )
    logging.info(f"Listening on {config.get('SST Server', 'host')}:{config.getint('SST Server', 'port')}")

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        pass


if __name__=='__main__':
    main()