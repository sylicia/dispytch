#
#    Modular REST API dispatcher in Python (dispytch)
#
#    Copyright (C) 2015 Denis Pompilio (jawa) <denis.pompilio@gmail.com>
#    Copyright (C) 2015 Cyrielle Camanes (cycy) <cyrielle.camanes@gmail.com>
#
#    This file is part of dispytch
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, see <http://www.gnu.org/licenses/>.

import ConfigParser
import os

EXIT_CFG_SYNTAX=1

_CONF_NAME='dispytch.conf'

_config_dict = {}

def _get_file_path():
    """Get file path

    :return: path
    :rtype: string
    """
    return os.path.sep.join([os.path.dirname(__file__), _CONF_NAME])


def _load_config_file():
    """Load config file

    Configuration file dispytch.conf should be in dispytch directory
    
    :return: ConfigParser
    """
    config_file = _get_file_path()
    conf_parser = ConfigParser.RawConfigParser()

    if not os.path.isfile(config_file) or not os.access(config_file, os.R_OK):
        print('File {0} not found or not readable'.format(config_file))
        exit(EXIT_CFG_SYNTAX)

    try:
        conf_parser.read(config_file)
    except ConfigParser.ParsingError as e:
        print(e.message)
        exit(EXIT_CFG_SYNTAX)

    return conf_parser


def _parse_conf():
    """Parse configuratiguration file and translate it as structure

    :return: Configuration
    :rtype: dict
    """
    conf_parser = _load_config_file()

    for section in conf_parser.sections():
        _config_dict.update({section : {}})
        for option in conf_parser.options(section):
            value = conf_parser.get(section, option)
            _config_dict[section].update({option : value})

def print_section(section):
    """Print section as comment to be human readable

    :param section str: selected section
    :return: section in human readable mode
    :rtype: str
    """
    conf = "# Section : {0}\n#===================\n".format(section)
    for opt in _config_dict.get(section):
        conf += "#  - opition {0} : {1}\n".format(opt,_config_dict[section][opt])

    print(conf)

def get_sections():
    """Get list of sections

    :return: list of sections
    :rtype: list
    """
    return _config_dict.keys()

def get_section(section):
    """Get options of specific section

    :param section string: name of the section
    
    :return: options
    :rtype: dict
    """
    return _config_dict.get(section)


def dispatch_list():
    """Get list of sections where dispatch value is set

    :return: list of sections with dispatch value
    :rtype: dict
    """
    dispatch_dict = {}

    for section in _config_dict:
        if _config_dict[section].has_key('dispatch'):
            value = _config_dict[section].get('dispatch')
            dispatch_dict.update({section : value})

    return dispatch_dict


def get_dispatch(dispatch):
    """Get section info of dispatch

    :param dispatch string: dispatch from which info is useful

    :return: related section with options
    :rtype: tuple
    """
    for section in _config_dict:
        if _config_dict[section].has_key('dispatch'):
            value = _config_dict[section].get('dispatch')
            if value == dispatch:
                return (section, _config_dict[section])

    return (None, {})


def logging():
    """Generate logging configuration

    :return: logging configuration to apply
    :rtype: dict
    """
    log = get_section('logging')
    log_level = log.get('level', 'debug').upper()
    log_format = log.get('format',
                     '%(asctime)s %(name)s [%(levelname)s] %(message)s')

    log_conf = {
        'version': 1,
        'formatters': {
            'simple': {
                'format': log_format 
            },
        },
        'handlers': {
            'null': {
                'class': 'logging.NullHandler',
            },
        },
        'loggers': {
            'dispytch': {
                'level': log_level,
                'handlers': ['null'],
                'propagate': 'no',
            },

        },
    }

    if log.get('console') == 'yes':
        log_conf['handlers'].update({
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            },
        })
        log_conf['loggers']['dispytch']['handlers'].append('console')

    if len(log.get('file', '')):
        log_conf['handlers'].update({
            'file': {
                'class': 'logging.FileHandler',
                'level': log_level,
                'formatter': 'simple',
                'filename': log.get('file'),
            },
        })
        log_conf['loggers']['dispytch']['handlers'].append('file')


    return(log_conf)


# Automatic load of configuration
_parse_conf()