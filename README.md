# Liquid watcher

This is an API server with one endpoint that returns a list of addresses with their up-to-date asset balances.

## Requirements

* Python 3.7
* Pip
* Virtualenv

## Install on Linux

Build the libwally python library for Linux:

```sh
$ bash scripts/build_wally_dist_linux
```

The script uses Docker to build the libwally python wheel and puts it into `wally_dist/` directory.

## Install on OSX

Build the libwally python library for Darwin:

```sh
$ bash scripts/build_wally_dist_darwin
```

## Install dependencies

```sh
$ virtualenv -p python3 .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.<os>.txt
```

The following flag arguments must be passed to start the server:

* `--datadir` the directory where to find `addresses.json` that contains the list of confidential addresses to watch
* `--network` either `mainnet`, `testnet` or `regtest` Liquid network
* `--esplora-url` of esplora API server
* `--asset` the hash of the asset to watch
* `--port` the port where to expose the API server

Example:

```sh
(.venv) $ python3 main.py --datadir /abs/path/to/datadir --network testnet --esplora-url https://blockstream.info/testnet/api --asset <asset_hash> --port 3333
```

The server exposes the endpoint `GET /balances` to get the *address,balance* pair list.

NOTE:  
The file `addresses.json` must contain a list of confidential addresses.  
The server creates a `balances.json` into datadir that uses to store the last up-to-date balance of any given address.  

## Using with Docker

After creating the dist with `scripts/build_wally_dist_linux`, you can skip the dependencies installation by running:

```sh
$ docker build -t liquid-watcher-linux:latest -f resources/Docekrfile .
$ docker run -v path/to/datadir:/config -p <port>:<port> [--network <docker_network_with_esplora_node>] -it liquid-watcher-linux:latest /bin/bash
<container-id> $ source .venv/bin/activate
<container-id> $ python main.py --datadir /config --port <port> ...
```

You must provide an external volume as the datadir where to find the address list JSON file.  
If you want to use a private esplora node such as Nigiri chopsticks, you should pass the `--network` to the container in order to add it to the docker network and use the ip assigned to that service. Remembere, `localhost` does not work on docker network.  
If you want to use a public esplora node such as blockstream.info, you don't need to specify the docker network.
