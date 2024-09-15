from neffytron.cog.settings.context import N_Context
from typing import Any, TypeVar
from neffytron.cog.settings.protocols import (
    DataSource,
    Interface,
    Node,
    ds_is_readable,
    ds_is_writable,
)

T = TypeVar("T")


class Branch(Node):
    """
    | A Node with children in the settings tree
    | you don't need to subclass this directly when defining a cog's settings
    | as it creates a Branch if there's no specified superclass
    """

    def __init__(self, context: N_Context, path=True):
        if path:
            self._n_context = context.add_path(self.__class__.__name__)
        else:
            self._n_context = context

    def __getattribute__(self, name: str, instance: bool = True):
        next = object.__getattribute__(self, name)
        if name.startswith("_"):
            return next
        # Pretend as if we did name(Branch) instead of name
        if len(next.__mro__) == 2:
            next = type(name, (next, Branch), {})
        return next(self._n_context) if instance else next

    def __setattr__(self, name: str, value: Any) -> None:

        # Allow setting the context
        if name in ["_n_context"]:
            object.__setattr__(self, name, value)
            return

        # Get the next object and let it decide how to set itself
        if name in dir(self):
            next_class = self.__getattribute__(name, False)
            if "_n_set" in dir(next_class):
                try:
                    next_class._n_set(next_class, value, self._n_context)
                    return
                except NotImplementedError:
                    pass
        # If we're the root node
        # (The only actually named Branch, I think, not going to check)
        # (:bap:able behaviour if you decide to name a node Branch to be able to set stuff on it)
        # (But this check is at the end of the function so if for some reason you do that, it'll still work)
        if self.__class__.__name__ == "Branch":
            object.__setattr__(self, name, value)
            return
        raise AttributeError(
            f"{self.__class__.__name__}.{name} Doesn't support setting"
        )


# Leaves
# These classes *only* define the shape of the data,
# using protocols to handle the what and how of storage
# which is done via jank dependency injection via superclasses

# I prefer to use CS/maths nomanculture over python
# e.g. Array over list...


class Value(Node, Interface, DataSource):
    """
    | A single value
    """

    # i.e. getter
    def __new__(cls, context: N_Context):
        if not issubclass(cls, ds_is_readable):
            raise NotImplementedError()
        context = context.add_path(cls.__name__)
        db_val = cls._d_get(cls, context)
        return cls._i_get(cls, db_val, context)

    def _n_set(self, x: T, context: N_Context) -> None:
        if not isinstance(self, ds_is_writable):
            raise NotImplementedError()
        str = self._i_set(self, x, context)
        self._d_set(self, str, context)
