'''
config.py: Handle Documentarist configuration commands

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020-2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   appdirs import user_config_dir
from   argparse import ArgumentParser, RawDescriptionHelpFormatter
from   commonpy.file_utils import readable, writable, copy_file
from   configparser import ConfigParser
from   os import makedirs
from   os.path import exists, join, dirname

from   documentarist.command import Command, method_parser
from   documentarist.exceptions import CannotProceed
from   documentarist.exit_codes import ExitCode
from   documentarist.log import log, loglist
from   documentarist.ui import UI, inform, warn, alert

# Constants.
# .............................................................................

# Default configuration values, in the absence of anything else.
DEFAULT_SETTINGS = {
    'documentarist': {
        'quiet'       : False,
        'debug'       : False,
        'basename'    : 'document',
        'outputdir'   : '.'
    },
    'google': {
        'creds_file': '',
    },
    'microsoft': {
        'creds_file': '',
    },
    'amazon': {
        'creds_file': '',
    },
}

# The configuration directory for Documentarist for this user account on the
# current computer.  This varies by operating system.  Know values are:
#   macOS:  ~/Library/Application Support/Documentarist/
#   Linux:  ~/.config/documentarist/
CONFIG_DIR = user_config_dir('Documentarist', 'CaltechLibrary')

# The default name of a configuration file that Documentarist will look for in
# its installation directory if not explicitly given a configuration file to
# use. The file must be in the format understood by Python 3's ConfigParser,
# (c.f. https://docs.python.org/3/library/configparser.html).
SETTINGS_FILE = 'documentarist.ini'

# The names of files for service credentials.
CREDENTIALS_FILES = {
    'amazon'    : 'amazon_credentials.json',
    'google'    : 'google_credentials.json',
    'microsoft' : 'microsoft_credentials.json',
}


# Class definitions.
# .............................................................................

class ConfigStorage():
    '''Configuration storage class.'''

    _config = ConfigParser(allow_no_value = True)
    _config_file = join(CONFIG_DIR, SETTINGS_FILE)

    def __init__(self):
        # Always begin by loading the built-in defaults. Any config loaded
        # afterwards or set via the command line will override the defaults.
        self._config.read_dict(DEFAULT_SETTINGS)


    @staticmethod
    def load(file = None):
        '''Loads a configuration from a file.
        If no argument is given, it attempts to load a default configuration
        files, looking first in the current directory and then in the program
        configuration directory identified by the constant CONFIG_DIR.
        '''
        if file and exists(file):
            log('loading configuration from file ' + file)
            ConfigStorage._config.read(file)
        else:
            ConfigStorage._config.read(ConfigStorage._config_file)


    @staticmethod
    def save(file = None):
        '''Save the current configuration values in the config file.'''
        if not exists(ConfigStorage._config_file):
            log('creating config dir ' + CONFIG_DIR)
            makedirs(CONFIG_DIR, exist_ok = True)
        file_path = file or ConfigStorage._config_file
        with open(file_path, 'w') as output_file:
            log('writing config file ' + file_path)
            ConfigStorage._config.write(output_file)


    @staticmethod
    def get(name, section = 'documentarist'):
        '''Returns the value of configuration variable 'name'.'''
        return ConfigStorage._config.get(section, name)


    @staticmethod
    def set(name, value, section = 'documentarist'):
        '''Sets the value of configuration variable 'name' to 'value'.
        If 'value' is None, nothing is done; the value None is a no-op.
        '''
        if name in ConfigStorage._config[section]:
            if not value:
                log(f'no new value given for {section}.{name} -- leaving as-is')
                return
            value = str(value)
            if ConfigStorage._config[section][name] != value:
                log(f'setting {section}.{name} to {value}')
                ConfigStorage._config[section][name] = str(value)
                ConfigStorage.save()
            else:
                log(f'{section}.{name} value unchanged: {value}')
        else:
            raise KeyError(f'Unknown config variable name: {name}')


    @staticmethod
    def settings():
        '''Return a multiline string summarizing the current config.'''
        entries = []
        for section_name, section in ConfigStorage._config.items():
            for var, value in ConfigStorage._config[section_name].items():
                entries.append((f'{section_name}.{var}', value))
        return entries


    @staticmethod
    def log_settings():
        '''Log all the current settings to the log stream.'''
        log(f'configuration:')
        loglist(f'  {var} = {value}' for var, value in Config.settings())


class ConfigCommand(Command):
    '''Set or show Documentarist's configuration.

    Documentarist has a number of configuration parameters that control its
    behavior.  The values of the parameters are stored in configuration files
    located in one of these directories (depending on the OS):

         ~/Library/Application Support/Documentarist/ (macOS) or
         ~/.config/documentarist/ (Linux)

    The configuration parameter values can be inspected and set using the
    "config" command. Changed values are persisted by storing them in the
    configuration file kept in the directory noted above.
    '''

    def __init__(self, arg_list):
        super().__init__('config')
        super()._invoke_with(arg_list)


    def show(self, args):
        '''Print the current configuration and exit.'''
        if args:
            settings = dict(Config.settings())
            for name in args:
                if name in settings:
                    print(f'{name} = {settings[name]}')
                else:
                    warn(f'Unrecognized setting name: {name}')
        else:
            for var, value in Config.settings():
                print(f'{var} = "{value}"')


    def basename(self, args):
        '''Set the basename for files downloaded over the network.

        When the inputs are URLs, Documentarist must download a copy of the
        image located at the network address (because it is not possible to
        write the results in the network locations represented by the URLs).
        The image at networked locations will be converted to ordinary PNG
        format for maximum compatibility with the different OCR services and
        written to files whose root names have the form "document-N.png",
        where "N" is an integer.  The URL corresponding to each document will
        be written in a file named "document-N.url" so that it is possible to
        connect each "document-N.png" to the URL it came from.

        The root name can be changed to something other than "document" using
        the "config basename" command.  For example,

            dm config basename someothername

        will change the naming pattern to "someothername-N".
        '''
        parser = method_parser(self.basename, summary = 'config basename <name>')
        parser.add_argument('name', action = 'store')
        if not args or 'help' in args:
            parser.print_help()
            return
        subargs = parser.parse_args(args)
        if subargs.name:
            ConfigStorage.set('basename', subargs.name)
            ConfigStorage.save()


    def outputdir(self, args):
        '''Set the output directory where files will be written.

        When processing images, Documentarist writes the results to new files
        that it creates either in the same directories as the original files,
        or alternatively, to a directory set by the command "config
        outputdir".  When an output directory has not been set and the input
        images are given as URLs, then the files are written to the current
        working directory instead.  The "config outputdir" command takes a
        directory path as its argument.  For example,

            dm config outputdir /tmp

        will change the output directory to /tmp.
        '''
        parser = method_parser(self.outputdir, summary = 'config outputdir <path>')
        parser.add_argument('path', action = 'store')
        if not args or 'help' in args:
            parser.print_help()
            return
        subargs = parser.parse_args(args)
        if subargs.path:
            if not exists(subargs.path):
                alert(f'Directory does not exist: {subargs.path}')
                raise CannotProceed(ExitCode.file_error)
            elif not writable(subargs.path):
                alert(f'Directory is not writable: {subargs.path}')
                raise CannotProceed(ExitCode.file_error)

            ConfigStorage.set('outputdir', subargs.path)
            ConfigStorage.save()


    def auth(self, args):
        '''Configure credentials for cloud services.

        Before a given service can be used, Documentarist needs to be
        supplied with user credentials for accessing that service.  The
        credentials must be stored in a JSON file with a certain format; see
        the Documentarist documentation for details about the formats for
        each service.  To add a new credentials file, use the "config auth"
        option in combination with the name of a service and a single file
        path on the command line.  The name supplied right after the "config
        auth" option must be the name of a recognized service, and the file
        argument must be a JSON file containing the credentials data in the
        required format for that service.  Here is an example of adding
        credentials for Google (assuming you created the JSON file as
        described in the docs):

          dm config auth google mygooglecreds.json

        Run dm with the "config auth" command separately to install
        credentials for each service.  Documentarist will copy the
        credentials to its configuration file and exit without doing anything
        else.
        '''
        parser = method_parser(self.auth, summary = 'config auth <service> <file.json>')
        parser.add_argument('service', nargs = 1, action = 'store',
                            help = 'service name ("google", "microsoft", or "amazon")')
        parser.add_argument('file', nargs = '?', action = 'store',
                            help = 'JSON file containing service credentials ')
        subargs = parser.parse_args(args)
        if not args or 'help' in args:
            parser.print_help()
            return
        service = subargs.service[0].lower()
        if service not in ['google', 'microsoft', 'amazon']:
            alert(f'Uncrecognized service name: {service}')
            raise CannotProceed(ExitCode.bad_arg)
        elif not subargs.file:
            alert(f'Missing file argument after service name.')
            raise CannotProceed(ExitCode.bad_arg)
        elif not subargs.file.endswith('json'):
            alert(f'File is expected to be a JSON file.')
            raise CannotProceed(ExitCode.bad_arg)
        else:
            dest_file = join(CONFIG_DIR, credentials_filename(service))
            copy_file(subargs.file, dest_file)
            ConfigStorage.set('creds_file', dest_file, service)


    # def cluster(self, args):
    #     '''Configure a cluster of worker nodes to use Ray.'''

    #     parser = ArgumentParser(description = 'Config a cluster',
    #                             usage = '%(prog)s config cluster config.yaml',
    #                             add_help = False)
    #     parser.add_argument('file', action = 'store',
    #                         help = 'YAML file containing Ray cluster configuration')
    #     subargs = parser.parse_args(args)
    #     if hasattr(subargs, 'file') and subargs.file == 'help':
    #         parser.print_help()
    #     elif subargs.file:
    #         # FIXME
    #         pass


# Utilities
# .............................................................................

def credentials_filename(service):
    assert service in CREDENTIALS_FILES
    return CREDENTIALS_FILES[service]


# Exported symbols.
# .............................................................................

Config = ConfigStorage()
