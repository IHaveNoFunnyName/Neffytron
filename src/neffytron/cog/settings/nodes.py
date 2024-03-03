
import io
import pprint
from typing import Iterator, List, Optional, TypeVar, Union, Generic
from attr import dataclass
from pymongo.database import Database
import discord
from discord.ext.commands import Context as DiscordContext
from prettytable import PrettyTable

# Here be all the hidden complexity


class Context:
    # Add dependencies here and in baseCog.py's cog_before_invoke if needed
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

    def _message(self, settings: 'ModuleSettings' = None):
        return self._node()._message(settings)


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
        next = getattr(self.settings, self.child)
        await interaction.response.edit_message(
            **next._message(next))


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
    _filter = {}

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

    def __len__(self):
        return self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(True)].count_documents(filter=self._filter)

    def _query(self, query):
        # For subclasses to override
        return self._to_store(query)

    def __contains__(self, item):
        return self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(True)].find_one(self._query(item))

    def __iter__(self) -> Iterator[StoredObject]:
        return [self._from_store(x) for x in self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(True)].find()].__iter__()

    def add(self, item):
        self.raw_add(self._to_store(item))

    def raw_add(self, item):
        self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') +
                         self._path.str(True)].insert_one(item)

    def delete(self, query):
        self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') +
                         self._path.str(True)].delete_many(self._to_store(query))

    def filter(self, query):
        self._filter = self._query(query)
        return self

    def find(self, query):
        return self._context.db[((str(self._context.discord.guild.id) + '.') if self._server else '') + self._path.str(True)].find(self._query(query))


class Binary_Relation(Array_Unordered):
    # Maths stuff in programming terms: Given sets A and B, their Cartesian product is [[a, b] for a in A for b in B]
    # A relation is a subset of the Cartesian product
    # tl;dr this is intended to store a bunch of [a, b] and test if it contains [x, y]

    # All its attributes have to impliment .list (returning all elements) and .options (returning {label, value} for each element)
    def __new__(cls, _: StoredObject):
        class __Binary_Relation(_Binary_Relation):
            _child = _
        return __Binary_Relation


class _Binary_Relation(_Array_Unordered):

    def _from_store(self, item):
        result = dotdict()
        for key in dir(self._child):
            if not key.startswith('_'):
                if key not in item:
                    raise ValueError('Invalid key ' + key)
                # This section added
                if item[key] == 'any':
                    result[key] = 'any'
                else:
                    # This section added
                    result[key] = getattr(self._child, key).get(
                        item[key], self._context)
        return result

    def add(self, item):
        # When adding a new item, don't add it if it's already in the relation
        if item not in self:
            super().add(item)

    def _message(self_root, settings: ModuleSettings = None):
        selects = []
        state = {}
        for name in dir(self_root._child):
            if not name.startswith('_'):
                child = getattr(self_root._child, name)
                selects.append(child.select(
                    self_root._context, name, state, True))

        class view(discord.ui.View):

            @discord.ui.button(
                style=discord.ButtonStyle.primary, label='Add', row=1)
            async def add_callback(self_view, parent_interaction: discord.Interaction, button: discord.ui.Button):
                class view(discord.ui.View):
                    @discord.ui.button(
                        style=discord.ButtonStyle.primary, label='Add', row=4)
                    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                        for name in dir(self_root._child):
                            if not name.startswith('_'):
                                if name not in state:
                                    state[name] = 'any'
                                    return
                        if state not in self_root:
                            self_root.add(state)
                        await interaction.message.delete()
                        await parent_interaction.message.edit(
                            **self_root._message(settings))

                    @discord.ui.button(
                        style=discord.ButtonStyle.danger, label='Cancel', row=4)
                    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                        await interaction.message.delete()

                message_view = view()
                for select in selects:
                    message_view.add_item(select)
                await parent_interaction.response.send_message('Add a new entry', view=message_view)

            @discord.ui.select(
                placeholder='Select entries to edit/delete', row=2, min_values=0, options=[discord.SelectOption(label=str(i), value=i) for i in range(len(self_root))]
            )
            async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                pass

            @discord.ui.button(
                style=discord.ButtonStyle.danger, label='Delete', row=3
            )
            async def delete_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                pass

            @discord.ui.button(
                style=discord.ButtonStyle.secondary, label='Edit', row=3
            )
            async def edit_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                pass

        table = PrettyTable()
        table.field_names = ['n'] + [name for name in dir(
            self_root._child) if not name.startswith('_')]
        for i, item in enumerate(self_root):
            row = [i]
            for name in item:
                if item[name] == 'any':
                    row.append('any')
                else:
                    row.append(getattr(self_root._child, name).display_name(
                        item[name], self_root._context))
            table.add_row(row)
        content = f'```{table.get_string()}```'
        return {'content': content, 'view': view()}

    def _query(self, query):
        for item in query:
            if query[item] == 'any':
                del query[item]
        query = self._to_store(query)
        for item in query:
            query[item] = {'$in': [query[item], 'any']}
        return query


class meta_array(type):
    # This isn't intutive - You do Interface[Val] and get out a Val
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
    _display_name = 'Default'
    _select_placeholder = 'Select an option'

    @classmethod
    def set(cls, x: T, context: Context) -> str:
        return NotImplementedError()

    @classmethod
    def get(cls, x: str, context: Context) -> T:
        return NotImplementedError()

    @classmethod
    def list(cls, context: Context) -> List[T]:
        return NotImplementedError()

    @classmethod
    def display_name(cls, x: T, context: Context) -> str:
        return NotImplementedError()

    @classmethod
    def options(cls, context: Context, any: bool = False):
        return ([{'label': 'Any', 'value': 'any'}] if any else []) + [{'label': cls.display_name(x, context), 'value': cls.set(x, context)} for x in cls.list(context)]

    @classmethod
    def select(cls, context: Context, name: str, state: dict, any: bool = False):
        # any: adds an 'any' option with a value of 'any' to the start of the list
        class Dropdown(discord.ui.Select):
            def __init__(self):
                options = [discord.SelectOption(
                    label=x['label'], value=x['value']) for x in cls.options(context, any)]
                super().__init__(placeholder=cls._display_name + ': ' + cls._select_placeholder,
                                 options=options)

            async def callback(self, interaction: discord.Interaction):
                state[name] = self.values[0]
                await interaction.response.defer()
        return Dropdown()


class str_interface(Interface, str):
    @classmethod
    def set(cls, x: str, context: Context) -> str:
        return x

    @classmethod
    def get(cls, x: str, context: Context) -> str:
        return x


class channel_interface(Interface, discord.TextChannel):
    _display_name = 'Channel'
    _select_placeholder = 'Select a channel'

    @classmethod
    def set(cls, x: discord.TextChannel, context: Context) -> str:
        return str(x.id)

    @classmethod
    def get(cls, x: str, context: Context) -> discord.TextChannel:
        # You know, after all this i no longer blame discord.py for not type hinting context
        return context.discord.guild.get_channel(int(x))

    @classmethod
    def list(cls, context: Context) -> List[discord.TextChannel]:
        return context.discord.guild.text_channels

    @classmethod
    def display_name(cls, x: discord.TextChannel, context: Context) -> str:
        return x.name

    @classmethod
    def select(cls, context: Context, name: str, state: dict, any: bool = False):
        class Dropdown(discord.ui.ChannelSelect):
            def __init__(self):
                super().__init__(placeholder=cls._display_name + ': ' +
                                 cls._select_placeholder + (' (leave empty for any)' if any else ''), min_values=0)

            async def callback(self, interaction: discord.Interaction):
                state[name] = self.values[0] if len(
                    self.values) else 'any'
                await interaction.response.defer()
        return Dropdown()


class member_interface(Interface, discord.Member):
    _display_name = 'Member'
    _select_placeholder = 'Select a member'

    @classmethod
    def set(cls, x: discord.Member, context: Context) -> str:
        return str(x.id)

    @classmethod
    def get(cls, x: str, context: Context) -> discord.Member:
        return context.discord.guild.get_member(int(x))

    @classmethod
    def list(cls, context: Context) -> List[discord.Member]:
        return context.discord.guild.members

    @classmethod
    def display_name(cls, x: discord.Member, context: Context) -> str:
        return x.display_name

    @classmethod
    def select(cls, context: Context, name: str, state: dict, any: bool = False):
        class Dropdown(discord.ui.UserSelect):
            def __init__(self):
                super().__init__(placeholder=cls._display_name + ': ' +
                                 cls._select_placeholder + (' (leave empty for any)' if any else ''), min_values=0)

            async def callback(self, interaction: discord.Interaction):
                state[name] = self.values[0] if len(
                    self.values) else 'any'
                await interaction.response.defer()
        return Dropdown()
