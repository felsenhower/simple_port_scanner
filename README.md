# simple_port_scanner

Simple HTTP server and client to test which ports are blocked between two machines.

## Dependencies

- Python (that's it)

## How it works

Imagine a situation like this:

```
Server            Internet           Mean Firewall       Client

┌────┐           .-,(  ),-.                              ┌────┐
╞════╡        .-(          )-.        ┌────────┐         │    │
│    │ ───── (                ) ───── │.. .....│ ─────   └────┘
│    │        '-(          ).-        └────────┘        ╱⠶⠶⠶╱
└────┘           '-.( ).--'                            ╶────╴
```

You are self-hosting a service on your webserver and wish to access this service with a client sitting behind a mean gateway out of your control that is blocking some ports. How do you find out which ports you can *actually* use to communicate between the client and the server?

Let's say your webserver is reachable via `123.123.123.123` and we want to answer this question for the ports between 4000 and 5000:

1. `server.py` is providing an HTTP server on a fixed "management port" (default: 3000)
2. `client.py` performs a `GET` on `http://123.123.123.123:3000/4000`.
3. `server.py` tries to open port `4000` for a second HTTP server and replies to the client, telling it wether the port was opened successfully.
4. If the port was opened successfully, `client.py` performs a `GET` on `http://123.123.123.123:4000/` with a timeout. If the request times out, let's assume that the firewall blocked it.
5. Repeat steps 2. to 4. with port 4001, 4002, ...

## How to use

### On the server-side

```bash
$ git clone https://github.com/felsenhower/simple_port_scanner.git
$ # Edit config.py to your liking...
$ ./server.py
```

### On the client-side

```bash
$ git clone https://github.com/felsenhower/simple_port_scanner.git
$ # Edit config.py to your liking...
$ ./client.py
$ # See the results in ports.txt
```

## Configuration

Edit `config.py` to your liking.

| | |
|-|-|
| `client.test_ports` | The range of ports you want to test. If you want to test ports below 1024, `server.py` needs to be run with root. |
| `client.timeout` | Timeout in seconds. Adjust according to your internet connection. |
| `client.sleep_between_requests` | Sleep time in seconds between requests. |
| `client.output_filename` | List of ports and their status. |
| `client.server_address` | Name that resolves to your webserver. Could be a domain (`http://example.com`) or an IP (`http://123.123.123.123`). |
| `management_port` | Which port to use to request opening other ports. Use a port that you already know is working. |
