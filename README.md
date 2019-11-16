# homenet

Find out when MAC addresses are on and off a home network.

# How to start

This project supports Python 3.5.2 so that it can run on a Raspberry Pi. Setup a Python virtual environment that runs Python 3.5.2

```python3.5.2 -m venv ./venv```

Then activate the virtual environment

```source ./venv/bin/activate```

Upgrade pip

```python -m pip install --upgrade pip```

Then install all the dependancies

```python -m pip install -r requirements.txt```

Then make a copy of `example_sys_settings.json` and name it `sys_settings.json`. Edit the `interface_name` value to match which network interface your device will be using to sniff for and send ARP requests/replys.

Then make a copy of `example_device_table.json` and name it `device_table.json`. Remove the entry in the `devices` key-value pair.

Then to run, open four terminals and navigate to the homenet directory with the Python scripts inside. Run one command per terminal. Make sure that you are running as root because the sockets package requires root access. Also make sure that each terminal is running your Python 3.5.2 environment.

```python
python comms.py
python smartarp.py listen
python smartarp.py send
python devicetable.py
```

# Examples

## Send ARP requests

Fill this in

## Listen and print ARP messages

Fill this in

## Send ARP requests to device and listen for response

Fill this in
