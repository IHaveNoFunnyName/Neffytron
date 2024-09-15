import pymongo.write_concern
from neffytron.cog.settings.context import N_Context
from neffytron.cog.settings.protocols import DataSource, ds_is_readable, ds_is_writable
import pymongo


class DS_wau(DataSource, ds_is_readable, ds_is_writable):

    def _d_get(self, context: N_Context):
        return "wau " + ".".join(context.path)

    def _d_set(self, x, context: N_Context):
        print("Sending :", x, " to the void", sep="")


class DS_mongo(DataSource, ds_is_readable, ds_is_writable):

    def _d_get(self, context: N_Context):
        path = ".".join(context.path[:-1])
        return context.db[path]["kv"].find_one({"key": self.__name__})["value"]

    def _d_set(self, x, context: N_Context):
        path = ".".join(context.path)
        context.db[path]["kv"].update_one(
            {"key": self.__name__},
            {"$set": {"value": x}},
            upsert=True,
        )
