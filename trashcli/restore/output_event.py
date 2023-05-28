from typing import NamedTuple, Union

Quit = NamedTuple('Quit', [])
Die = NamedTuple('Die', [('msg', Union[str, Exception])])
Println = NamedTuple('Println', [('msg', str)])
Exiting = NamedTuple('Exiting', [])
OutputEvent = Union[Quit, Die, Println, Exiting]
