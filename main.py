import sys
from collections import defaultdict, namedtuple

VERSION = '1.0'


class CommandParser():

    def __init__(self, application='', description='', epilog=''):
        self.command_map = defaultdict(list)
        self.help_map = {}

        self.default_error_handlers = [self._command_not_found_handler]
        self.default_error_message = 'Undefined command({}) called!'

        self._application = application
        self._description = description
        self._epilog = epilog

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

        self.help_map['/'.join(commands)] = str(help_message)

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

        # print(command, payload, args)
        return self._excute(command, payload, args)

    def _excute(self, command, payload, args):
        if command not in self.command_map:
            self._command_not_found_handler(command)
            return False

        for handler in self.command_map[command]:
            handler(payload, args)

        return True

    def _command_not_found_handler(self, error_command):
        print(self.default_error_message.format(error_command))

    def print_help(self):
        help_message = []
        help_message.append('usage: {}'.format(self._application))
        for command in self.help_map:
            help_message.append(' [{}]'.format(command))
        help_message.append('\n\n')
        help_message.append(self._description)

        for command, command_help in self.help_map.items():
            if command_help:
                help_message.append('{}: {}\n'.format(command, command_help))

        if self._epilog:
            help_message.append('\n')
            help_message.append(self._epilog)

        print(''.join(help_message))


class CommandHandler():

    def __init__(self):
        self._init_parser()

    def _init_parser(self):
        self.command_parser = CommandParser('To.do')
        self.command_parser.add_arguement(
            '-h', '--help',
            handlers=[self._help],
            help_message='Show this help')
        self.command_parser.add_arguement(
            '-v', '--version',
            handlers=[self._version],
            help_message='Show the version')
        self.command_parser.add_arguement(
            'add', '+',
            handlers=[self._add],
            help_message='''Add an todo tasks
    add [task_name] ... [-before/-b date] [-p priority] [-r Remarks]
    Required parameters
        [task_name]: This todo tasks's name
    Optional parameters
        [-before/-b date]: 'date' should be an legal date time, You will receive a reminder by the deadline
        [-p priority]: 'priority' should be an integer between 1 and 5
        [-r Remarks]: Add an remarks for this todo tasks''')
        self.command_parser.add_arguement(
            'today',
            handlers=[self._today],
            help_message='''Show the tasks you have to do today
        ''')
        self.command_parser.add_arguement(
            'tomorrow',
            handlers=[self._tomorrow],
            help_message='''Show the tasks you have to do tomorrow
        ''')
        self.command_parser.add_arguement(
            'show', 'list',
            handlers=[self._show],
            help_message='''Show all the tasks you have to do
        ''')
        self.command_parser.add_arguement(
            'done', 'finished', '*',
            handlers=[self._done],
            help_message='''Marked that you have completed this task
        ''')
        self.command_parser.add_arguement(
            'delete', 'del', '-',
            handlers=[self._delete],
            help_message='''Delete the task
        ''')

    def deal_with(self, string):
        ok = self.command_parser.parse(string)
        if not ok:
            self._help()

    def _help(self, *kwargs):
        self.command_parser.print_help()

    def _version(self, *kwargs):
        print('Version:', VERSION)

    def _add(self, *kwargs):
        pass
        # TODO: Add

    def _today(self, *kwargs):
        pass
        # TODO: Today

    def _tomorrow(self, *kwargs):
        pass
        # TODO: Tomorrow

    def _show(self, *kwargs):
        pass
        # TODO: Show

    def _done(self, *kwargs):
        pass
        # TODO: Done

    def _delete(self, *kwargs):
        pass
        # TODO: Delete


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
