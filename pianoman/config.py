#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import copy
import json
import pkgutil
import logging

from argparse import ArgumentParser


class Config(dict):

    _default_config = None
    _packagename = __module__.split('.')[0].replace('_', '')
    _prefix = '{}_'.format(_packagename.upper())
    _default_file_name = '{}.config.json'.format(_packagename)

    __doc__ = """
Config module takes parameters from command line, json files, environment, and the
default config json in this pacakge and presents a config object with dict interface
and direct accessors.  Default config is overidden by config file is overidden
by environment is overidden by command line and c'tor args.  Environment will pick
up any environment variables prefixed with "{}" Prefix can be overidden in module
get_config method.
    """.format(_prefix)

    def __init__(self, fname=None, **kwargs):
        if not fname:
            fname = os.path.join(os.getcwd(), self._default_file_name)
        self.update(self.make_config(self.get_default_config()))

        if os.path.exists(fname):
            self.update(json.load(open(fname, 'r')))
        else:
            logging.getLogger().info("Unable to find {}".format(fname))
        self.update(kwargs)

    def build_argparser(self, description="Argparser generated from config module"):
        parser = ArgumentParser(description=description,
                                conflict_handler='resolve')
        # TODO: eval should filter for poison inputs
        for d in self.get_default_config():
            name = "--{}".format(d.pop("name"))
            if 'default' in d:
                d['default'] = self.eval_default_value(d)
            if 'type' in d:
                if d['type'] in ('list', 'dict'):
                    d['nargs'] = '+'
                d.pop('type')
            parser.add_argument(name, **d)

        parser.add_argument(
            '-c', '--config', default="./{}.config.json".format(self._prefix.lower()),
            action='store', dest='configfile',
            help=self.__doc__)

        return parser

    def override(self, kvdict, skipdefaults=False):
        defaults = {}
        ff = lambda x: str(defaults.get(x, '__' + str(kvdict[x]))) != str(kvdict[x])
        if skipdefaults:
            defaults = self.make_config(self.get_default_config())
        if kvdict:
            self.update({k: kvdict[k] for k in filter(ff, kvdict)})
        return self

    def as_dict(self):
        return copy.deepcopy(self)

    def as_environment_dict(self):
        return {self._prefix + k: str(v) for k, v in self.items()}

    def get(self, item, *argv):
        if item in self:
            return self.__getitem__(item)
        return dict.get(self, item, *argv)

    def __getitem__(self, item):
        val = dict.__getitem__(self, item)
        if type(val) is str:
            return val.format_map(self)
        return val

    def __setitem__(self, item, val):
        specd = self.get_default_config_as_dict()
        if item in specd:
            return super().__setitem__(item, self.eval_default_value(specd[item], val))
        return super().__setitem__(item, val)

    def __iter__(self, *args, **kwargs):
        return super(self).__iter__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return super(self).__iter__(*args, **kwargs)

    def update(self, d):
        specd = self.get_default_config_as_dict()
        ud = {k: self.eval_default_value(specd.get(k), v)
              if k in specd else v for k, v in d.items()}
        super().update(ud)

    def __getattr__(self, name):
        if name in self:
            return self.__getitem__(name)
        return super().__getitem__(name)

    @classmethod
    def eval_default_value(clz, elem, val=None):
        defval = lambda: val if val else elem.get('default', None)
        if defval():
            if 'type' in elem and 'type' == eval("type({type}).__name__".format_map(elem)):
                if elem['type'] in ('list', 'dict'):
                    if type(defval()).__name__ == elem['type']:
                        return defval()
                    return eval(defval())
                return eval(elem['type'])(defval())
        return elem.get('default', val)

    @classmethod
    def make_config(clz, spec):
        return {d['name']: clz.eval_default_value(d) for d in spec}

    @classmethod
    def get_default_config(clz):
        if not clz._default_config:
            pkg = clz.__module__.split('.')[0]
            data = pkgutil.get_data(pkg, 'default.config.json')
            clz._default_config = json.loads(data.decode('UTF-8'))

        return copy.deepcopy(clz._default_config)

    @classmethod
    def get_default_config_as_dict(clz):
        return {i.get('name'): i for i in clz.get_default_config()}
