# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

"""
The Guard pattern ir a monad which helps improve code readability and
maintainability by avoiding nested if statements. Other advantages include:

- It is easy to add new conditions.
- It is easy to add new actions.
- It helps to avoid code duplication.
- It helps to avoid the use of exceptions for control flow.
- It helps standardize messages and error handling.

Example:

    >>> Guards.guard({
    ... 'name': 'age',
    ... 'value': 18,
    ... }, '!empty|lt[18]')
    fail('age must be greater than 18')

    >>> Guards.guard({
    ... 'name': 'age',
    ... 'value': 18,
    ... }, '!empty|le[18]')
    ok()

In the example above, the guard method receives a dictionary with the name and
value of the argument to be validated, and a string with the conditions to be
checked. The conditions are separated by the pipe character (|). The first
character of the condition is the operator. The rest of the condition is the
argument of the operator. The operators are:

- !: Negates the condition.
- between: Checks if the length of the value is between the arguments.
- empty: Checks if the value is empty.
- eq: Checks if the value is equal to the argument.
- even: Checks if the value is even.
- ge: Checks if the value is greater than or equal to the argument.
- gt: Checks if the value is greater than the argument.
- in: Checks if the value is in the list of arguments.
- length: Checks if the length of the value is equal to the argument.
- le: Checks if the value is less than or equal to the argument.
- lt: Checks if the value is less than the argument.
- negative: Checks if the value is negative.
- odd: Checks if the value is odd.
- positive: Checks if the value is positive.
- regex: Checks if the value matches the regular expression.
- required: Checks if the value is not None.

The operators can be combined using the pipe character (|). The conditions are
evaluated in order. If a condition fails, the evaluation stops and the error
message is returned. If all conditions pass, the evaluation stops and an empty
string is returned.

Argments can be passed to the operators using square brackets ([]). The
arguments are separated by semicolons (;). The arguments are evaluated in order.
If an argument is invalid, the evaluation stops and an error message is returned.
Are supported the following types of arguments:

- int: Integer.
- float: Floating point number.
- str: String.
- list: List of strings.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Union, Optional, TypedDict, NoReturn, Dict, Type, Tuple


class GuardArgument(TypedDict):
    """
    A wrapper for guard arguments.
    """
    name: str
    value: Any


@dataclass(frozen=True, eq=True)
class GuardResult:
    """
    A wrapper for guard results. A GuardResult is frozen and immutable.
    """

    def __init__(self, success: bool, message: Optional[str]):
        object.__setattr__(self, 'success', success)
        object.__setattr__(self, 'message', message)

    def is_satisfied(self):
        return object.__getattribute__(self, 'success')

    def get_message(self):
        return object.__getattribute__(self, 'message')

    def __bool__(self):
        return self.is_satisfied()

    def __repr__(self):
        if self.is_satisfied():
            return f'ok()'
        return f'fail({self.get_message()})'


"""
A type alias for raw arguments.
"""
RawArg = Union[bool, int, float, str, None]

"""
A type alias for complex arguments.
"""
ComplexArg = Union[List[RawArg], Tuple[RawArg, ...]]


class InvalidPunctuatorError(SyntaxError):
    """
    An exception for empty statements.
    """

    def __init__(self, statement: str, pos: int):
        self.statement = statement
        self.pos = pos

    def __str__(self):
        return f"Invalid statement at position {self.pos}:\n{self.statement}\n{' ' * (self.pos - 1)}^"


class ExpectedPunctuatorError(SyntaxError):
    """
    An exception for empty statements.
    """

    def __init__(self, statement: str, pos: int, expected: str):
        self.statement = statement
        self.pos = pos
        self.expected = expected

    def __str__(self):
        return f"Expected {self.expected} at position {self.pos}:\n{self.statement}\n{' ' * self.pos}^"


class StatementParser:
    """
    A wrapper for parsing statements.

    Sintax:

        - digit: [0-9]
        - nonzerodigit: [1-9]
        - nondigit: [a-zA-Z_]
        - integer: digit+
        - float: integer . integer
        - string: ".*?"
        - punctuator: [ ( , ) ] " |
        - escape: \\[ \\' \\" \\]
        - token: nondigit | nonzerodigit | integer | float | string |
            escape | punctuator | list | tuple | regex | token
        - list: [token, ...]
        - tuple: (token, ...)
        - regex: r"token"
        - guard: !token | token | token[token, ...] | token | guard

    Example:

        interger: 1
        >>> StatementParser().parse('1')
        1

        float: 1.0
        >>> StatementParser().parse('1.0')
        1.0

        string: 'hello'
        >>> StatementParser().parse('hello')
        'hello'

        list: [1, 2, 3]
        >>> StatementParser().parse('[1, 2, 3]')
        [1, 2, 3]

        tuple: (1, 2, 3)
        >>> StatementParser().parse('(1, 2, 3)')
        (1, 2, 3)

        regex: ^\\d+$
        >>> StatementParser().parse('^\\d+$')
        '^\\d+$'

        regex: r"^\\d+$, ^\\w+$"
        >>> StatementParser().parse('r"^\\d+$, ^\\w+$"')
        '^\\d+$, ^\\w+$'

        regex in lists:
        >>> StatementParser().parse('[r"^\\d+$", r"^\\w+$]"')
        ['^\\d+$', '^\\w+$']
    """

    def __init__(self, value: str):
        self.value = value
        self.pos = 0
        self.length = len(value)

    def _next(self, salt: int = 1) -> str:
        """
        Gets the next character.

        :return: Returns the next character.
        """
        if self.pos + salt - 1 < self.length:
            return self.value[self.pos: self.pos + salt]
        return ''

    def _skip(self, n: int = 1) -> NoReturn:
        """
        Skips n characters.

        :param n: The number of characters to skip.

        :return: Returns nothing.
        """
        self.pos += n

    def _skip_whitespace(self) -> NoReturn:
        """
        Skips whitespace characters.

        :return: Returns nothing.
        """
        while self._next().isspace():
            self._skip()

    def _skip_comma(self) -> NoReturn:
        """
        Skips comma character.

        :return: Returns nothing.
        """
        if self._next() == ',':
            self._skip()

    def _find(self, char: str) -> int:
        """
        Finds a character.

        :param char: The character to find.

        :return: Returns the position of the character.
        """
        return self.value.find(char, self.pos)

    def _parse_escape(self) -> str:
        """
        Parses an escape character.

        :return: Returns an escape character.
        """
        if self._next() == '\\':
            self._skip()
            return self._next()
        return ''

    def _is_escape(self) -> bool:
        """
        Checks if the next character is an escape character.

        :return: Returns True if the next character is an escape character,
        otherwise False.
        """
        return self._next() == '\\'

    def _is_punctuator(self) -> bool:
        """
        Checks if the next character is a punctuator.

        :return: Returns True if the next character is a punctuator,
        otherwise False.
        """
        return self._next() in ['(', ',', ')', '[', ']', '"', '|']

    def _end(self) -> bool:
        """
        Checks if the end of the string has been reached.

        :return: Returns True if the end of the string has been reached,
        otherwise False.
        """
        return self.pos >= self.length

    def _parse_token(self) -> Union[RawArg, ComplexArg]:
        """
        Parses a token.

        :return: Returns a token.
        """
        token = ''

        self._skip_whitespace()

        while not self._end() and not self._is_punctuator():
            if self._next() == '\\':
                self._skip()
                token += self._next()
            elif self._next() == '"':
                self._skip()
                break
            else:
                token += self._next()
            self._skip()

        if token == '':
            raise InvalidPunctuatorError(self.value, self.pos)

        match token.strip().lower():
            case 'true':
                return True
            case 'false':
                return False
            case 'none':
                return None
            case _:
                if token.isnumeric():
                    return int(token)
                elif re.match(r'^\d+\.\d+$', token):
                    return float(token)
                else:
                    return token

    def _expect_args_punctuator(self, punctuator: str, message: str) -> bool:
        """
        Checks if the next character is a punctuator. If the next character is
        a punctuator, it skips it.

        Raises:

            ExpectedPunctuatorError: If the next character is not a punctuator.

        :param punctuator: The punctuator to check.
        :param message: The error message.

        :return: Returns True if the next character is a punctuator, otherwise
        False.
        """
        self._skip_whitespace()

        if self._end():
            raise ExpectedPunctuatorError(self.value, self.pos, message or ' or '.join(punctuator))

        if self._next() in punctuator:
            return True

        return False

    def _parse_list(self) -> List[Union[RawArg, ComplexArg]] | None:
        """
        Parses a list.

        :return: Returns a list.
        """

        if self._next() == '[':
            self._skip()

            items = []

            while True:
                if self._expect_args_punctuator('][(r', 'Expected closing bracket ]'):
                    self._skip()
                    break

                if self._next() == ',':
                    self._skip()

                items = self._parse_args()

            return items

        return None

    def _parse_tuple(self) -> Tuple[Union[RawArg, ComplexArg], ...] | None:
        """
        Parses a tuple.

        :return: Returns a tuple.
        """

        if self._next() == '(':
            self._skip()

            items = []

            while True:
                if self._expect_args_punctuator(')[(r', 'Expected closing parenthesis.'):
                    self._skip()
                    break

                if self._next() == ',':
                    self._skip()

                items.append(self._parse_args())

            return tuple(*items)

        return None

    def _parse_regex(self) -> str | None:
        """
        Parses a regex.

        :return: Returns a regex.
        """
        regex = ''

        if self._next(2) == 'r"':
            self._skip(2)

            while True:
                if self._end():
                    raise ExpectedPunctuatorError(self.value, self.pos, '"')

                _next = self._next()

                if _next == '\\':
                    regex += self._parse_escape()
                elif _next == '"':
                    self._skip()
                    break
                else:
                    regex += _next

                self._skip()

        return regex

    def _parse_args(self) -> List[Union[RawArg, ComplexArg]]:
        """
        Parses a list of arguments.

        :return: Returns a list of arguments.
        """
        args = []

        while True:
            if self._expect_args_punctuator('])', 'Expected closing ] or )'):
                break

            if self._next() == ',':
                self._skip()
                self._skip_whitespace()

            match self._next():
                case '[':
                    args.append(self._parse_list())
                case '(':
                    args.append(self._parse_tuple())
                case 'r':
                    args.append(self._parse_regex())
                case _:
                    args.append(self._parse_token())

        return args

    def _parse_guard(self) -> Tuple[bool, str, List[Union[RawArg, ComplexArg]]]:
        """
        Parses a guard.

        Guard syntax:

            - !: Negates the guard.
            - name: The guard name.
            - args: The guard arguments.

        Format:

            - !?([a-zA-Z0-9_]*)(?:\\[(.*?)])?

            The args are optional. If the args are not provided, the guard
            arguments will be an empty list. The args can be a list of arguments
            separated by commas (,). The args punctuators are '[' ot '('.

        :return: Returns a guard.
        """
        negate = False
        args = []

        if self._next() == '!':
            negate = True
            self._skip()

        name = self._parse_token().strip()

        # the next punctuator must be [ ot (
        if self._next() in ['[', '(']:
            self._skip()
            args = self._parse_args()
            self._skip()

        return negate, name, args

    def parse(self) -> List[Tuple[bool, str, List[Union[RawArg, ComplexArg]]]]:
        """
        Parses a string to guard list. The guard string are separated by pipe
        character (|)

        Syntax:

            - guard: !?([a-zA-Z0-9_]*)(?:\\[(.*?)])?
            - guards: guard(?:\\|guard)*

        :return: Returns a guard list.
        """

        guards = []

        while True:
            self._skip_whitespace()

            if self._end():
                break

            if self._next() == '|':
                self._skip()
                self._skip_whitespace()

            guards.append(self._parse_guard())

        return guards


class IGuarder(ABC):
    """
    An interface for rules.
    """

    @abstractmethod
    def is_satisfied_by(self, *args) -> GuardResult:
        """
        Validates an argument.
        """
        ...

    @classmethod
    def new(cls, *args) -> 'IGuarder':
        """
        Creates a new instance of the rule.

        :param args: The rule arguments.

        :return: Returns a new instance of the rule.
        """
        ...

    def parse(self, **kwargs) -> str:
        """
        Parses the rule to string.

        :return: Returns a string.
        """
        ...


class Guards:
    """
    A wrapper for guards. The Guards class is static and immutable.
    """

    """
    A dictionary of guards.
    """
    __guards__: Dict[str, Type[IGuarder]] = {}

    def __new__(cls):
        raise Exception("Cannot instantiate Guards class")

    @classmethod
    def register(cls, name: str, guarder: Type[IGuarder]) -> NoReturn:
        """
        Registers a guard. The guarders must be unique by name.

        Raises:

            KeyError: If the guard already exists.

        :param name: The guard name.
        :param guarder: The guard class.

        :return: Returns nothing.
        """
        if cls.has(name):
            raise KeyError(f"Guard {name} is already defined in Guarder")

        cls.__guards__[name] = guarder

    @classmethod
    def get(cls, name: str) -> Type[IGuarder]:
        """
        Gets a guard by name.

        Raises:

            KeyError: If the guard does not exist.

        :arg name: The guard name.

        :return: Returns a guard.
        """
        return cls.__guards__[name]

    @classmethod
    def has(cls, name: str) -> bool:
        """
        Checks if a guard exists.

        :param name: The guard name.

        :return: Returns True if the guard exists, otherwise False.
        """
        return name in cls.__guards__

    @classmethod
    def resolve(cls, statement: str) -> List[IGuarder]:
        """
        Resolves a guard by name.

        Raises:

            KeyError: If the guard does not exist.

        :param statement: The guard statement.

        :return: Returns a guard.
        """

        try:
            parser = StatementParser(statement)

            raw_guards = parser.parse()

            guards = []

            for raw in raw_guards:
                if not cls.has(raw[1]):
                    raise KeyError(f"Guard {raw[1]} is not defined in Guarder")

                guards.append(cls.get(raw[1]).new(*raw))

            return guards

        except SyntaxError as e:
            print(str(e))

    @classmethod
    def guard(
            cls,
            arg: GuardArgument,
            statement: str,
            message: Optional[str] = None
    ) -> GuardResult:
        """
        Validates an argument against a list of guards. This function
        receive a string or list as guards, parses and invokes them.

        guards format:

        name: Must be a sequence of alphabetic characters (a-zA-Z).
        args: Can be True, False, None or a sequence of alphanumeric
        characters (“a-zA-Z0-9”).
        negate: Can be an exclamation mark (!) to indicate negation.
        separator: Can be a pipe character (|) to separate multiple guards.
        guard: It is the combination of negate, name and args.

        Usage Example: The string “!required|!empty|length[1, 10]” represents
        three guards. The first guard is “required” with negation, the second
        is “empty” also with negation, and the third is “length” with arguments
        “1, 10”.

        :param arg: The guard argument.
        :param statement: Guard string.
        :param message: A personalized message in case of an error.

        :return: Returns a GuardResult.
        """

        try:
            guards = cls.resolve(statement)

            for g in guards:
                result = g.is_satisfied_by(arg)

                if not result:
                    if message:
                        return GuardResult(False, message)
                    return result

            return GuardResult(True, None)
        except Exception as e:
            print(e)

    @staticmethod
    def combine(results: List[GuardResult]) -> GuardResult:
        """
        Combines a list of GuardResults into a single GuardResult. If any
        of the GuardResults are failures, the first failure will be returned.

        :param results: The list of GuardResults.

        :return: If it has failures in list, returns the first fail,
        otherwise, return True.
        """
        for result in results:
            if not result.is_satisfied():
                return result
        return GuardResult(True, None)


def guard(arg: GuardArgument, guards: str, message: Optional[str] = None) -> GuardResult:
    """
    Validates an argument against a list of guards. This function
    receive a string or list as guards, parses and invokes them.

    Guards Format:

        name: Must be a sequence of alphabetic characters (a-zA-Z).
        args: Can be True, False, None, list, tuple, or a regex.
        negate: Can be an exclamation mark (!) to indicate negation.

        Arguments are optional. If the arguments are not provided, the guard
        arguments will be an empty list or tuple. The arguments can be a list of arguments

        Usage Example: The string “!required|!empty|between[1, 10]|regex[r"\\w+"]|length(1)” represents
        three guards. The first guard is “required” with negation, the second
        is “empty” also with negation, the third is “between” with arguments
        “1, 10”, the fourth is “regex” with arguments “r"\\w+"”, and the fifth is “length” with arguments
        "1" in tuple format.

    Syntax:

        - digit: [0-9]
        - nonzero-digit: [1-9]
        - integer: digit+
        - float: integer . integer
        - string: ".*?"
        - punctuator: [ ( , ) ] " |
        - escape: \\[ \\' \\" \\]
        - token: nonzero-digit | integer | float | string |
            escape | punctuator | list | tuple | regex | token
        - list: [token, ...]
        - tuple: (token, ...)
        - regex: r"token"
        - guard: !token | token | token[token, ...] | token(token, ...) | token | guard

    Example:

        >>> Guards.guard({
        ... 'name': 'age',
        ... 'value': 18,
        ... }, '!empty|lt[18]')
        fail('age must be greater than 18')

        >>> Guards.guard({
        ... 'name': 'age',
        ... 'value': 18,
        ... }, '!empty|le(18)')
        ok()

    Default guards:

        format: name [ args:type, ... ]

        required: Test if the value is not None.
        empty: Test if the value is empty.
        length[expected:int]: Test if the length of the value is equal to the expected.
        between[min:int, max:int]: Test if the length of the value is between the min and max.
        regex[regex:str]: Test if the value matches the regular expression.
        le[max:int]: Test if the value is less than or equal to the max.
        lt[max:int]: Test if the value is less than the max.
        ge[max:int]: Test if the value is greater than or equal to the max.
        gt[max:int]: Test if the value is greater than the max.
        in[list:List[ComplexArg]]: Test if the value is in the list.
        odd: Test if the value is odd.
        even: Test if the value is even.
        positive: Test if the value is positive.
        negative: Test if the value is negative.
        eq[expected:ComplexArg]: Test if the value is equal to the expected.


    :param message: A personalized message in case of an error.
    :param arg: The guard argument.
    :param guards: guard string or guard list.

    :return: Returns a GuardResult.
    """
    return Guards.guard(arg, guards, message)


def guard_all(
        values: Dict[str, Any],
        guards: Dict[str, str],
        messages: Dict[str, str] = None

) -> GuardResult:
    """
    Guards all arguments in a dictionary. Equivalent as calling the guard
    function for each argument in the dictionary and combine result.
    See the guard function for more guards information.

    :param values: the dict containing values
    :param guards: the dict containing guards
    :param messages: the dict containing custom messages

    :return: A combination of guard results
    """

    results = []

    for key, value in values.items():
        if key in guards:
            results.append(guard(
                {
                    'name': key,
                    'value': value
                },
                guards[key],
                messages[key] if messages and key in messages else None
            ))

    return combine(results)


def combine(results: List[GuardResult]) -> GuardResult:
    """
    Combines a list of GuardResults into a single GuardResult. If any
    of the GuardResults are failures, the first failure will be returned.

    :param results: The list of GuardResults.

    :return: If it has failures in list, returns the first fail,
    otherwise, return True.
    """
    return Guards.combine(results)


def guarder(name: str) -> NoReturn:
    """
    A decorator for registering rules.
    """

    def decorator(cls: Type[IGuarder]):
        Guards.register(name, cls)

    return decorator


class AbstractGuard(IGuarder):
    """
    An abstract class for rules.
    """

    """
    The error message.
    """
    message: str = ''

    """
    The guard arguments.
    """
    args: List[Union[RawArg, ComplexArg]]

    """
    The guard name.
    """
    name: str = ''

    """
    The guard negation.
    """
    negation: str = 'not'

    def __init__(self, negate: bool, name: str, args: List[Union[RawArg, ComplexArg]] = None):
        self.negate = negate
        self.name = name
        self.args = args or []

    @abstractmethod
    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        """
        Validates an argument.
        """
        ...

    def parse(self, **kwargs) -> str:
        """
        Parses the arguments to a string.

        Injections:

            negation: Inject the negation (not) if the guard is negated.
            custom: Inject custom arguments in key-value format.

        Example:

            >>> Required(True, 'name').parse()
            'name not is required'

            >>> Length(False, 'name', [1]).parse({'length': 10})
            'name must be of length 10'

        :param kwargs: Custom injections.

        :return: Returns a string.
        """

        cls = type(self)

        injections = {
            'name': self.name,
            'not': ' ' + cls.negation + ' ' if self.negate else ' ',
            **kwargs
        }

        return self.message.format(**injections)

    @classmethod
    def new(cls, *args) -> 'IGuarder':
        """
        Creates a new instance of the rule.

        :param args: The rule arguments.

        :return: Returns a new instance of the rule.
        """
        return cls(*args)


@guarder(name='required')
class Required(AbstractGuard):
    """
    Validates that the argument is not None.
    """

    message = '{name}{not}is required'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value is None or self.negate:
            return GuardResult(False, self.parse(name=argument['name']))

        return GuardResult(True, None)

    def __repr__(self):
        return f"Required({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='empty')
class Empty(AbstractGuard):
    """
    Validates that the argument is empty.
    """

    message = '{name} must{not}be empty'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if len(value) > 0 or self.negate:
            return GuardResult(False, self.parse(name=argument['name']))

        return GuardResult(True, None)

    def __repr__(self):
        return f"Empty({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='length')
class Length(AbstractGuard):
    """
    Validates that the argument has a specific length.
    """

    message = '{name} must{not}have of length {length}'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if len(value) != self.args[0] or self.negate:
            return GuardResult(False, self.parse(name=argument['name'], length=self.args[0]))

        return GuardResult(True, None)

    def __repr__(self):
        return f"Length({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='between')
class Between(AbstractGuard):
    """
    Validates that the argument has a length between two values.
    """

    message = '{name} must{not}be between {min} and {max}'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if len(value) < self.args[0] or len(value) > self.args[1] or self.negate:
            return GuardResult(False, self.parse(name=argument['name'], min=self.args[0], max=self.args[1]))

        return GuardResult(True, None)

    def __repr__(self):
        return f"Between({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='regex')
class Regex(AbstractGuard):
    """
    Validates that the argument matches the regular expression.
    """

    message = '{name} must{not}match the regular expression {regex}'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if not re.match(self.args[0], value) or self.negate:
            return GuardResult(False, self.parse(name=argument['name'], regex=self.args[0]))

        return GuardResult(True, None)

    def __repr__(self):
        return f"Regex({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='in')
class In(AbstractGuard):
    """
    Validates that the argument is in the list.
    """

    message = '{name} must{not}be in the list {list}'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value not in self.args[0] or self.negate:
            return GuardResult(False, self.parse(name=argument['name'], list=self.args[0]))

        return GuardResult(True, None)

    def __repr__(self):
        return f"In({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='le')
class LessThanOrEqual(AbstractGuard):
    """
    Validates that the argument is less than or equal to the value.
    """

    message = '{name} must{not}be less than or equal to {max}'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value > self.args[0] or self.negate:
            return GuardResult(False, self.parse(name=argument['name'], max=self.args[0]))

        return GuardResult(True, None)

    def __repr__(self):
        return f"LessThanOrEqual({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='lt')
class LessThan(AbstractGuard):
    """
    Validates that the argument is less than the value.
    """

    message = '{name} must{not}be less than {max}'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value >= self.args[0] or self.negate:
            return GuardResult(False, self.parse(name=argument['name'], max=self.args[0]))

        return GuardResult(True, None)

    def __repr__(self):
        return f"LessThan({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='ge')
class GreaterThanOrEqual(AbstractGuard):
    """
    Validates that the argument is greater than or equal to the value.
    """

    message = '{name} must{not}be greater than or equal to {min}'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value < self.args[0] or self.negate:
            return GuardResult(False, self.parse(name=argument['name'], min=self.args[0]))

        return GuardResult(True, None)

    def __repr__(self):
        return f"GreaterThenOrEqual({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='gt')
class GreaterThan(AbstractGuard):
    """
    Validates that the argument is greater than the value.
    """

    message = '{name} must{not}be greater than {min}'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value <= self.args[0] or self.negate:
            return GuardResult(False, self.parse(name=argument['name'], min=self.args[0]))

        return GuardResult(True, None)

    def __repr__(self):
        return f"GreaterThan({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='odd')
class Odd(AbstractGuard):
    """
    Validates that the argument is odd.
    """

    message = '{name} must{not}be odd'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value % 2 == 0 or self.negate:
            return GuardResult(False, self.parse(name=argument['name']))

        return GuardResult(True, None)

    def __repr__(self):
        return f"Odd({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='even')
class Even(AbstractGuard):
    """
    Validates that the argument is even.
    """

    message = '{name} must{not}be even'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value % 2 != 0 or self.negate:
            return GuardResult(False, self.parse(name=argument['name']))

        return GuardResult(True, None)

    def __repr__(self):
        return f"Even({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='positive')
class Positive(AbstractGuard):
    """
    Validates that the argument is positive.
    """

    message = '{name} must{not}be positive'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value <= 0 or self.negate:
            return GuardResult(False, self.parse(name=argument['name']))

        return GuardResult(True, None)

    def __repr__(self):
        return f"Positive({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='negative')
class Negative(AbstractGuard):
    """
    Validates that the argument is negative.
    """

    message = '{name} must{not}be negative'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value >= 0 or self.negate:
            return GuardResult(False, self.parse(name=argument['name']))

        return GuardResult(True, None)

    def __repr__(self):
        return f"Negative({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()


@guarder(name='eq')
class Equal(AbstractGuard):
    """
    Validates that the argument is equal to the value.
    """

    message = '{name} must{not}be equal to {value}'

    def is_satisfied_by(self, argument: GuardArgument) -> GuardResult:
        value = argument['value']

        if value != self.args[0] or self.negate:
            return GuardResult(False, self.parse(name=argument['name'], value=self.args[0]))

        return GuardResult(True, None)

    def __repr__(self):
        return f"Equal({self.negate}, {self.args})"

    def __str__(self):
        return self.__repr__()
