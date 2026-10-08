from abc import abstractmethod

from tests.support.list_abstract_methods import list_abstract_methods
from trashcli.compat import Protocol

class TestListAbstractMethods:
    def test_list(self):
        class A(Protocol):
            @abstractmethod
            def method2(self):
                pass
            @abstractmethod
            def method1(self):
                pass
            def non_abstract_method(self):
                pass

        assert list_abstract_methods(A) == {'method1', 'method2'}

    def test_list__when_hiearchy__should_show_all_the_methods(self):
        class ParentProtocol(Protocol):
            @abstractmethod
            def method1(self):
                pass

        class SonProtocol(ParentProtocol, Protocol):
            @abstractmethod
            def method2(self):
                pass

        assert list_abstract_methods(SonProtocol) == {'method1', 'method2'}
