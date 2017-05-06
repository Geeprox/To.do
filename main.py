import sys
from collections import defaultdict, namedtuple

VERSION = '1.0'


class CommandParser():

    def __init__(self):
        self.command_map = defaultdict(list)
        self.help_map = {}

        self.default_error_handlers = [self._command_not_found_handler]
        self.default_error_message = 'Undefined command called'

    def _verify_command_type(self, command):
        if not isinstance(command, str):
            raise TypeError('Parameter "command" should be str')

    def _verify_handler_type(self, handler):
        if not callable(handler):
            raise TypeError('Handler should be callable')

    def add_arguement(self, *commands, handlers, help_message=''):
        for command in commands:
            self._verify_command_type(command)
            if command in self.command_map:
                raise ValueError(
                    'Command({}) should not be added another time'.format(command))

        if not isinstance(handlers, list):
            raise TypeError('Parameter "handlers" should be a list')

        for handler in handlers:
            self._verify_handler_type(handler)

        for command in commands:
            self.command_map[command].extend(handlers)
            self.help_map[command] = str(help_message)

    def parse(self, items):
        try:
            command = items[0]
        except KeyError:
            for handler in self.default_error_handlers:
                handler()
            return False

        payload = []
        args = {}
        StateMachine = namedtuple(
            'StateMachine', ['idle', 'found_args'])
        state_machine = StateMachine(1, 2)
        state = state_machine.idle
        arg_cache = ''

        for read in items[1:]:
            read = str(read).strip()
            if state == state_machine.idle:
                if read.startswith('-'):
                    state = state_machine.found_args
                    arg_cache = read
                else:
                    payload.append(read)
            elif state == state_machine.found_args:
                if read.startswith('-'):
                    if arg_cache not in args:
                        args[arg_cache] = True
                    arg_cache = read
                else:
                    state = state_machine.idle
                    args[arg_cache] = read
                    arg_cache = ''
        if arg_cache:
            args[arg_cache] = True

        return self._excute(command, payload, args)

    def _excute(self, command, payload, args):
        try:
            handlers = self.command_map[command]
        except KeyError:
            return False

        for handler in handlers:
            handler(payload, args)

        return True

    def add_hook(self, command, handler):
        try:
            self._verify_command_type(command)

            if command not in self.command_map:
                raise ValueError(
                    'Command({}) should been added'.format(command))

            self._verify_handler_type(handler)
        except (TypeError, ValueError):
            return False

        self.command_map[command].insert(0, handler)
        return True

    def _command_not_found_handler(self):
        raise ValueError(self.default_error_message)

    def print_help(self):
        help_message = 'Help'
        # TODO: Build help message
        print(help_message)


class CommandHandler():

    def __init__(self):
        self._init_parser()

    def _init_parser(self):
        self.command_parser = CommandParser()
        self.command_parser.add_arguement(
            '-h', '--help', handlers=[self._help])
        self.command_parser.add_arguement(
            '-v', '--version', handlers=[self._version])

    def deal_with(self, string):
        self.command_parser.parse(string)

    def _help(self, *kwargs):
        self.command_parser.print_help()

    def _version(self, *kwargs):
        print('Version:', VERSION)

    def add(self, args):
        print('add called')

    def today(self, args):
        print('Today:')

    def tomorrow(self):
        print('Tomorrow')


def main():
    def system_call():
        command_handler.deal_with(sys.argv[1:])

    def self_call():
        while True:
            command = input()
            command_handler.deal_with(command.split())

    command_handler = CommandHandler()

    if len(sys.argv) == 1:
        self_call()
    else:
        system_call()


if __name__ == '__main__':
    main()
