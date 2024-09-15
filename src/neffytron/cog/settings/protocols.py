from typing import List, Protocol, TypeVar, runtime_checkable

from neffytron.cog.settings.context import N_Context
from neffytron.utils import n_discord_message
from discord import ActionRow

# I would far prefer to colocate protocols at the top of their respective files
# but python *hates* circular dependencies so this is safer.

T = TypeVar("T")

# As the `class` keyword is the only python language construct
# (I know of)
# that supports the simple and readable nesting structure of children I want
# Anything you want to be type hinted should be @classmethod
# And also everything's green in the IDE

# At runtime they are replaced with the actual data you would expect

# Also I'm lying this isn't just protocols but also base class implimentation
# (Where appropriate)

# I'm lying again as we check if something subclasses a protocol, so it's closer to interfaces or mixins


# Interfaces
# _i_ namespace


class Interface(
    Protocol
    # , T
):
    """
    | Defines each object that can be stored and retrieved
    | Currently the only remote data type is str
    | Inherit from the stored type also and enjoy type hints :)
    | file://./interface.py
    """

    @classmethod
    def _i_set(cls, x: T, context: N_Context) -> str:
        """Converts the object to a string for storage"""
        return x

    @classmethod
    def _i_get(cls, x: str, context: N_Context) -> T:
        """Constructs the object from a string"""
        return x

    @classmethod
    def _i_display_value(cls, x: T, context: N_Context) -> str:
        """Representative value for the admin view, limit TODO chars"""
        raise NotImplementedError()

    @classmethod
    def _i_admin_edit(cls, x: T, context: N_Context) -> ActionRow:
        """
        | Admin view to edit the value
        | Annoyingly there's no plain text/label component
        | Will be used by itself and alongside other rows depending on the Structure
        | I guess just use a disabled select menu?
        | A button that opens a modal can be used for text input
        """
        raise NotImplementedError()


class Selectable_Interface(Interface):
    """
    | Interface for objects that can be selected from a list
    """

    @classmethod
    def _i_array(cls, context: N_Context) -> list[T]:
        """
        | List of all possible values
        | Only used for its ActionRow,
        | so can be left unimplemented if not needed
        | e.g. for discord channels.
        """
        raise NotImplementedError()

    @classmethod
    def _i_admin_set(cls, x: T, context: N_Context) -> ActionRow:
        return super().admin_set(x, context)


# Data Sources
# _d_ namespace


class DataSource(Protocol):
    """
    | Defines a source of data for the settings object
    | E.G. MongoDB, discord pins, message author, etc...
    | really anything as long as you can put it in Context
    | file://./source.py
    """


# Data Source Mixins


@runtime_checkable
class ds_is_readable(Protocol):
    """
    | Data source that can be read from
    """

    @classmethod
    def _d_get(cls, N_Context) -> str:
        """
        | Get the value from the source
        | Keep in mind this will be called
        | as both an instance and class method
        """
        raise NotImplementedError()


@runtime_checkable
class ds_is_writable(Protocol):
    """
    | Data source that can be written to
    """

    @classmethod
    def _d_set(cls, x: str, context: N_Context) -> None:
        """
        | Set the value in the source
        | Keep in mind this will be called both
        | as an instance and class method
        """
        raise NotImplementedError()


@runtime_checkable
class ds_is_arrayable(Protocol):
    """
    | Data source that can store arrays
    """

    def _d_array(cls, context: N_Context) -> List[T]:
        pass

    @classmethod
    def __len__(cls):
        pass


@runtime_checkable
class ds_is_array_findable(Protocol):
    """
    | Data source that can find a single value in an array
    """

    def _d_find(cls, x: T, context: N_Context) -> T:
        pass


# Nodes
# _n_ namespace
class Node(Protocol):
    """
    | \_namespaced\_ attributes are implimentation stuff,
    | non-\_namespaced\_ attributes are the actual data/settings
    | file://./node.py
    """

    _n_context: N_Context

    def __init__(cls, context: N_Context):
        super.__init__(context)

    def _n_set(cls, x: T, context: N_Context) -> None:
        """
        | Set the value in the data source
        """
        raise NotImplementedError()

    def _n_admin_message(cls, context: N_Context) -> n_discord_message:
        """
        | Message to display in the admin view
        | Should include the current value and an edit button
        """
        pass


# see file://./node.py
