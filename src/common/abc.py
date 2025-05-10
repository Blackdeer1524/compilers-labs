import abc


class IGraphVizible(abc.ABC):
    @property
    def node_name(self) -> str:
        return f"{self.__class__.__name__}{id(self)}"

    @abc.abstractmethod
    def to_graphviz(self) -> str:
        return f'\t{self.node_name} [label="{self.__class__.__name__}"]\n'
