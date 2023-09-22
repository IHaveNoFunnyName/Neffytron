
from typing import Optional, TypeVar, Union
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
        if len(self.key): newpath.append(self.key)

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
            if (issubclass(attr, Leaf)):
                return attr(self._context, self._path.append(key)).__get__(self, self)
            return ModuleSettings(attr, self._context, self._path.append(key))
        
    def __setattr__(self, key, value):
        if(hasattr(self._node, key)):
            attr = getattr(self._node, key)
            if (issubclass(attr, Leaf)):
                attr(self._context, self._path.append(key)).__set__(self, value)
            return
        else:
            super().__setattr__(key, value)
    
    def _message(self):
        return self._node()._message()

class Node:
    def _message(self):
        view = discord.ui.View()
        for child in self._dir():
            name = getattr(self, child)._display if '_display' in dir(
                getattr(self, child)) else child

            view.add_item(NodeButton(name, 1, self))

        content = (self.path[-1] if len([]) else '')
        return {'content': content, 'view': view}

    def _dir(self):
        return [x for x in dir(self) if not x.startswith('_')]


class NodeButton(discord.ui.Button):
    def __init__(self, label, row, node, style=discord.ButtonStyle.primary):
        super().__init__(style=style, label=label, row=row)
        self.node = node

    async def callback(self, interaction: discord.Interaction):
        pass

# I don't think the type var actually constrains the children at all, but I guess it makes it clear what to do from the dev end
# I could actually look up how people do interfaces in python but whatever
# Base class works for strings
T = TypeVar('T')
class InterfaceDB:
    def set(x: T, context: Context) -> str:
        return x
    def get(x: str, context: Context) -> T:
        return x

class DB_Channel(InterfaceDB):
    def set(x: discord.TextChannel, context: Context) -> str:
        return str(x.id)
    def get(x: str, context: Context) -> discord.TextChannel:
        # You know, after all this i no longer blame discord.py for not type hinting context
        return context.discord.guild.get_channel(int(x))

class Leaf(Node):
    def __init__(self, context: Context, path: Path):
        self._context = context
        self._path = path
    
    _default = None
    _server = True

class DB_Array(Leaf):
    _default = []

    def __contains__(self, item):
        search = {}
        for key in item:
            if key not in self._dir():
                return False
            val = item['key']
            if type(val) != str:
                if 'id' not in val:
                    return False
            search['key'] = val

        self.db[self.path].find_one()

class MCGetItem(type):
    def __getitem__(cls, index: InterfaceDB):
        _DB_Value = type('_DB_Value', (DB_Value,), {'_interface': index})
        return _DB_Value

class DB_Value(Leaf, metaclass=MCGetItem):
    _interface = InterfaceDB

    def __get__(self, instance, owner):
        entry = self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(False)].kv.find_one(
            {'key': self._path.key})
        return self._interface.get(entry['value'], self._context) if entry is not None else self._default

    def __set__(self, instance, value):
        value = self._interface.set(value, self._context)
        self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(False)].kv.find_one_and_replace(
            {'key': self._path.key}, {'key': self._path.key, 'value': value}, upsert=True)