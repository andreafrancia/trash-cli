from typing import NamedTuple, Text, Union

Quit = NamedTuple('Quit', [])
Die = NamedTuple('Die', [('msg', Union[Text, Exception])])
Println = NamedTuple('Println', [('msg', str)])
Exiting = NamedTuple('Exiting', [('msg', str)])
OutputEvent = Union[Quit, Die, Println, Exiting]
