import abc


class IGraphVizible(abc.ABC):
    @property
    def node_name(self) -> str:
        return f"{self.__class__.__name__}{id(self)}"

    @property
    def node_label(self) -> str:
        return self.__class__.__name__

    @abc.abstractmethod
    def to_graphviz(self) -> str:
        return f'\t{self.node_name} [label="{self.node_label}"]\n'
