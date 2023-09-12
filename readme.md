# Neffytron

I suppose I should make this public.

## Setup

Create a virtual enviroment 
```
python -m venv /venv/
```
Activate it
```
(linux) source ./venv/bin/activate
```
Install requirements into the venv
```
pip install -r requirements.txt
```

Install the neffytron package into the venv
```
pip install -e .
```
Intstall mongodb and set it up

Copy `.env.example` to `.env` and fill it out

Run it and marvel at how it logs into discord and sets up some permission stuff that does nothing

## DB

Acess to a mongodb database is provided for Cogs through accessing the `Settings` cog.

I made a mistake and tried using mongodb, thinking that I would be able to treat nested BSON as its own database... But instead it's only 1 layer deep. Oh well.
I had set it up by the time I realised it wasn't going to be what I wanted, but I continued because sunk cost and I'm sure 'Did something with mogodb' looks nice CV wise.

I blame the one tutorial I read that talked about accessing collections through `x.y.z`, neglecting to mention that that's just... the name of the collection, not children.

### Schema

Database name `neffytron`. Collections are named `{Guild ID}.{Cog}.{collection}`, with each cog only having full access to its own collections. A `global` Guild ID will eventually be made once there's some functionality that would benefit from it.

`collection = settings` provides key value storage with a simple get/setter for Cogs to access.

Other collections can be used for whatever the cog wants, currently only supports find/upsert one, but more will be written when they would be useful.

~~and since the only current Cog's name is Settings... this means that one collection is called `{Guild ID}.settings.settings`. Great~~
