from typing import NamedTuple, Union

Quit = NamedTuple('Quit', [])
Die = NamedTuple('Die', [('msg', str)])
Println = NamedTuple('Println', [('msg', str)])
Exiting = NamedTuple('Exiting', [])
OutputEvent = Union[Quit, Die, Println, Exiting]
