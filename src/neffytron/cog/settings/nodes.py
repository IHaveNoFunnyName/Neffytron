
from typing import Iterator, Optional, TypeVar, Union, Generic
from attr import dataclass
from pymongo.database import Database
import discord
from discord.ext.commands import Context as DiscordContext

# Add more stuff here as needed


class Context:
    def __init__(self, discord: DiscordContext, db: Database):
        self.discord = discord
        self.db = db


class Path:
    def __init__(self, path: Union[list[str], str], key: str):
        if type(path) == str:
            if path == '':
                path = []
            else:
                path = [path]
        self.path = path
        self.key = key

    def append(self, key: str):
        newpath = self.path.copy()
        if len(self.key):
            newpath.append(self.key)

        return Path(newpath, key)

    def str(self, include_key: bool = True):
        return '.'.join(self.path) + ('.' + self.key if include_key else '')


class ModuleSettings:
    def __init__(self, node: 'Node', context: Context, path: Optional[Path]):
        self._context = context
        self._node = node
        self._path = path if path is not None else Path([], '')

    def __getattr__(self, key: str):
        if not key.startswith('_') and hasattr(self._node, key):
            attr = getattr(self._node, key)
            # Because i'm doing metaclass stuff I can't just check if it's a subclass of Leaf, but you can treat this as equivalent
            if (issubclass(attr, (Leaf, Interface))):
                obj = attr(self._context, self._path.append(key))
                obj._default = attr._default
                return obj.__get__(self, self) if '__get__' in dir(obj) else obj
            return ModuleSettings(attr, self._context, self._path.append(key))

    def __setattr__(self, key, value):
        if (hasattr(self._node, key)):
            attr = getattr(self._node, key)
            # Because i'm doing metaclass stuff I can't just check if it's a subclass of Leaf, but you can treat this as equivalent
            if (issubclass(attr, (Leaf, Interface))):
                obj = attr(self._context, self._path.append(key))
                obj._default = attr._default
                return obj.__set__(self, value) if '__set__' in dir(obj) else obj
            return
        else:
            super().__setattr__(key, value)

    def _message(self):
        return self._node()._message(self)


class Node:
    def _message(self, settings: ModuleSettings = None):
        view = discord.ui.View()
        for child in self._dir():
            name = getattr(self, child)._display if '_display' in dir(
                getattr(self, child)) else child

            view.add_item(NodeButton(name, 1, settings, child))

        content = self._description if '_description' in dir(self) else ''
        return {'content': content, 'view': view}

    def _dir(self):
        return [x for x in dir(self) if not x.startswith('_')]


class NodeButton(discord.ui.Button):
    settings: ModuleSettings

    def __init__(self, label, row, settings: ModuleSettings, child: str, style=discord.ButtonStyle.primary):
        super().__init__(style=style, label=label, row=row)
        self.settings = settings
        self.child = child

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            **getattr(self.settings, self.child)._message())


class Leaf(Node):
    def __init__(self, context: Context, path: Path):
        self._context = context
        self._path = path

    _default = None
    _server = True


class Val(Leaf):
    _interface: 'Interface'

    def __get__(self, instance, owner):
        entry = self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(False)].kv.find_one(
            {'key': self._path.key})
        return self._interface.get(entry['value'], self._context) if entry is not None else self._default

    def __set__(self, instance, value):
        value = self._interface.set(value, self._context)
        self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(False)].kv.find_one_and_replace(
            {'key': self._path.key}, {'key': self._path.key, 'value': value}, upsert=True)


class dotdict(dict):
    __getattr__ = dict.get
    # Raise errors on these
    def __setattr__(): raise NotImplementedError('Immutable')
    def __delattr__(): raise NotImplementedError('Immutable')


StoredObject = TypeVar('StoredObject')


class Array_Unordered(Generic[StoredObject]):
    # I can't believe just this breaks intellisense lmao
    def __new__(cls, _: StoredObject):
        class __Array_Unordered(_Array_Unordered):
            _child = _
        return __Array_Unordered

    # Dummy attrs for intellisense
    def __init__(self, _: StoredObject):
        pass

    def __iter__(self) -> Iterator[StoredObject]:
        pass

    def __contains__(self, item: StoredObject) -> bool:
        pass

    def add(self, item: StoredObject) -> None:
        pass

    def delete(self, query: StoredObject) -> None:
        pass

    def find(self, query: StoredObject) -> Iterator[StoredObject]:
        pass


class _Array_Unordered(Leaf):
    _default = []
    _child = None

    def _to_store(self, item):
        result = dotdict()
        for key in item:
            if key not in dir(self._child):
                raise ValueError('Invalid key ' + key)
            result[key] = getattr(self._child, key).set(
                item[key], self._context)
        return result

    def _from_store(self, item):
        result = dotdict()
        for key in dir(self._child):
            if not key.startswith('_'):
                if key not in item:
                    raise ValueError('Invalid key ' + key)
                result[key] = getattr(self._child, key).get(
                    item[key], self._context)
        return result

    def __contains__(self, item):
        return self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(True)].find_one(self._to_store(item))

    def __iter__(self) -> Iterator[StoredObject]:
        return [self._from_store(x) for x in self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(True)].find()].__iter__()

    def add(self, item):
        self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') +
                         self._path.str(True)].insert_one(self._to_store(item))

    def delete(self, query):
        self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') +
                         self._path.str(True)].delete_many(self._to_store(query))

    def find(self, query):
        return self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(True)].find(self._to_store(query))


# This isn't intutive - You do Interface[Val] and get out a Val
class meta_array(type):
    def __getitem__(cls, index: 'Val'):
        return type('_DB_Value', (index,), {'_interface': cls})

    # When used by Array it's not an instance so this doesn't get called. Understandable.
    def __call__(cls, *args, **kwargs):
        return type('_DB_Value', (Val,), {'_interface': cls})(*args, **kwargs)


# I don't think the type var actually constrains the children at all, but I guess it makes it clear what to do from the dev end
# I could actually look up how people do interfaces in python but whatever

# Base class works for strings
T = TypeVar('T')


class Interface(metaclass=meta_array):
    def set(x: T, context: Context) -> str:
        return x

    def get(x: str, context: Context) -> T:
        return x

    def view_row(self, row: int):
        return discord.ui.Button(label=self._display, row=row, style=discord.ButtonStyle.secondary)

    def view_modal(self):
        pass


class str_interface(Interface, str):
    pass


class channel_interface(Interface, discord.TextChannel):
    def set(x: discord.TextChannel, context: Context) -> str:
        return str(x.id)

    def get(x: str, context: Context) -> discord.TextChannel:
        # You know, after all this i no longer blame discord.py for not type hinting context
        return context.discord.guild.get_channel(int(x))


class member_interface(Interface, discord.Member):
    def set(x: discord.Member, context: Context) -> str:
        return str(x.id)

    def get(x: str, context: Context) -> discord.Member:
        return context.discord.guild.get_member(int(x))
