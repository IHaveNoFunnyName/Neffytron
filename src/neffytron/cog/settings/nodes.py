
from typing import Optional, TypeVar, Union
from attr import dataclass
from pymongo.database import Database
import discord
from discord.ext.commands import Context as DiscordContext


def view_builder(schema: 'Node', path: Optional[list[str]] = None):
    if path is None:
        path = []

    node = schema
    for key in path:
        if key in dir(node):
            node = getattr(node, key)
        else:
            raise ValueError

    return node._view(node(), path, schema)

# Add more stuff here as needed
class Context:
    def __init__(self, discord: DiscordContext, db: Database):
        self.discord = discord
        self.db = db

class Path:
    def __init__(self, path: str, key: str):
        self.path = path
        self.key = key
    def append(self, key: str):
        return Path((self.path + '.' if len(self.path) else '') + self.key, key)


class ModuleSettings():
    def __init__(self, schema: 'Node', context: Context, path: Optional[Path]):
        self._context = context
        self._schema = schema
        self._path = path if path is not None else Path('', '')

    def __getattr__(self, key: str):
        if not key.startswith('_') and hasattr(self._schema, key):
            attr = getattr(self._schema, key)
            # Add ifs here for other data stores/node types
            if (issubclass(attr, Leaf)):
                return attr(self._context, self._path.append(key)).__get__(self, self)
            return ModuleSettings(attr, self._context, self._path.append(key))
        
    def __setattr__(self, key, value):
        if(hasattr(self._schema, key)):
            attr = getattr(self._schema, key)
            # Add ifs here for other data stores/node types
            if (issubclass(attr, Leaf)):
                attr(self._context, self._path.append(key)).__set__(self, value)
            return
        else:
            super().__setattr__(key, value)


class Node:
    # For the basic 'node' case, each view displays a list of buttons for its children
    class _view(discord.ui.View):
        def __init__(self, node: 'Node', path: list[str], schema: 'Node'):
            super().__init__()
            self.node = node
            self.path = path
            self.schema = schema

            for i, back in enumerate(path, 1):
                self.add_item(NodeButton(back, 0, self.schema,
                              path[:-i], style=discord.ButtonStyle.red))

            for child in node._dir():
                name = getattr(node, child)._display if '_display' in dir(
                    getattr(node, child)) else child

                new_path = path.copy()
                new_path.append(child)

                self.add_item(NodeButton(name, 1, self.schema, new_path))

            self.content = 'The Message Content' + \
                (self.path[-1] if len(self.path) else '')

    # Not confident to overwrite stuff for this
    def _dir(self):
        return [x for x in dir(self) if not x.startswith('_')]


class NodeButton(discord.ui.Button[Node._view]):
    def __init__(self, label, row, schema, path, style=discord.ButtonStyle.primary):
        super().__init__(style=style, label=label, row=row)
        self.schema = schema
        self.path = path

    async def callback(self, interaction: discord.Interaction):
        next_view = view_builder(self.schema, self.path)
        await interaction.response.edit_message(content=next_view.content, view=next_view)

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

class DB_Array(Leaf):
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
    _default = None

    class _view(Node._view):
        def __init__(self, node, path, schema):
            self.node = node
            self.path = path
            self.schema = schema

            self.content = self.__get__(None, None)

    def __get__(self, instance, owner):
        entry = self._context.db[self._path.path].values.find_one(
            {'key': self._path.key})
        return self._interface.get(entry['value'], self._context) if entry is not None else self._default

    def __set__(self, instance, value):
        value = self._interface.set(value, self._context)
        self._context.db[self._path.path].values.find_one_and_replace(
            {'key': self._path.key}, {'key': self._path.key, 'value': value}, upsert=True)