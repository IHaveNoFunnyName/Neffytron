
from typing import Optional
from pymongo.database import Database
import discord


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


class DB_Node(Node):
    def __init__(self, db: Database, path, key):
        self.db = db
        self.path = path
        self.key = key


class DB_Array(DB_Node):
    def __init__(self, db: Database, path, key):
        super().__init__(db, path, key)

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


class DB_Value(DB_Node):
    class _view(Node._view):
        def __init__(self, node, path, schema):
            self.node = node
            self.path = path
            self.schema = schema

            self.content = self.__get__(None, None)

    def __get__(self, instance, owner):
        entry = self.db[self.path].values.find_one(
            {'key': self.key})
        return entry['value'] if entry is not None else None

    def __set__(self, instance, value):
        self.db[self.path].values.find_one_and_replace(
            {'key': self.key}, {'key': self.key, 'value': value}, upsert=True)
