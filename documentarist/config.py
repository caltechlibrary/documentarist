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
from   bun import UI, inform, warn, alert, alert_fatal
from   configparser import ConfigParser
from   os.path import exists, join, dirname

from   documentarist.command import Command


# Constants.
# .............................................................................

CONFIG_FILE = 'documentarist.ini'
'''
The default name of a configuration file that Documentarist will look for in
its installation directory if not explicitly given a configuration file to use.
The file must be in the format understood by Python 3's ConfigParser,
(c.f. https://docs.python.org/3/library/configparser.html).
'''

CONFIG_DIR = user_config_dir('Documentarist', 'CaltechLibrary')
'''
The configuration directory for Documentarist for this user account on the
current computer.  This varies by operating system.  Know values are:
  macOS:  ~/Library/Application Support/Documentarist/
  Linux:  ~/.config/documentarist/
'''


# Exported classes.
# .............................................................................

class Config():
    _config = ConfigParser()
    _config_file = None

    def __init__(self):
        self._config.add_section('DEFAULT')


    @staticmethod
    def load(config_file):
        if config_file:
            Config._config_file = config_file
            Config._config.read(config_file)
        else:
            # Look for and maybe load default config file.
            alternatives = [CONFIG_FILE, join(CONFIG_DIR, CONFIG_FILE)]
            for file in alternatives:
                if exists(file):
                    Config._config_file = file
                    Config.load(file)
                    break


    @staticmethod
    def get(name, section = 'DEFAULT'):
        return Config._config.get(section, name)


    @staticmethod
    def set(name, value, section = 'DEFAULT'):
        if name in Config._config[section]:
            Config._config[section][name] = str(value)
        else:
            raise KeyError(f'Unknown config variable name: {name}')


    @staticmethod
    def settings():
        entries = [('DEFAULT.config_file', Config._config_file)]
        for section_name, section in Config._config.items():
            for var, value in Config._config[section_name].items():
                entries.append((f'{section_name}.{var}', value))
        return entries


class ConfigCommand(Command):
    '''Set or show Documentarist's configuration.

    Documentarist has a number of configuration parameters that control its
    behavior.  The values of the parameters can be set in a configuration file.
    Documentarist looks for a configuration file in the following locations
    each time it runs, in this order:

      1. the file given as the value of the --configfile option
      2. a file named "documentarist.ini" in the current directory
      3. a file named "documentarist.ini" either in the directory
         ~/Library/Application Support/Documentarist/ (macOS) or
         ~/.config/documentarist/ (Linux)

    The "config" commands can be used to display current configuration values
    as well as set configuration values.
    '''

    def __init__(self, args):
        super().__init__('config', args)


    def show(self, args):
        '''Print the current configuration and exit.'''
        print('invoked config show')


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

        print(f'in basename got {args}')
        parser = ArgumentParser(description = 'Set the basename for downloaded files',
                                usage = '%(prog)s config basename [-h] name')

        parser.add_argument('name', action = 'store')
        subargs = parser.parse_args(args)
        print(f'result = {subargs}')


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
        print('invoked config outputdir')


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
        print('invoked config auth')


    def color(self, args):
        '''Turn on or off coloring of terminal output.'''
        print('invoked config color')
