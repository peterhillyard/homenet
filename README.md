# homenet

Find out what MAC addresses are on and off a home network.

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

# How it all works

The homenet package provides a way for you to know when the last time a device was on a network. A device can be uniquely identified by its MAC address, and when that MAC address has been heard from recently, then you know that the device is nearby. Homenet forces devices to respond by sending ARP requests on the network. A device will respond to an ARP request by replying with a message that contains its MAC address and IP address. While Homenet is periodically sending ARP requests, it is also listening for ARP requests and replies. When Homenet gets an ARP packet, it parses the packet for the senders MAC address and IP address. These messages and some metadata are then sent to a Google Sheet which serves as the database.

## Breakdown of Homenet
Homenet is made up of 5 different parts: an ARP listener, an ARP sender, a device table manager, a database interface, and a message forwarder.

### ARP Listener
The ARP listener continuously looks for ARP messages that get sent on the network. The listener parses the ARP packets to get the sender's MAC and IP address. As long as the ARP packet is not a broadcast ARP message from the device that is running Homenet, then the ARP listener sends to the Forwarder a zmq message which contains the source and destination MAC and IP address contained in the ARP packet.

### ARP Sender
The ARP sender is responsible for periodically sending out ARP packets on the network so that devices on the network will respond with an ARP reply. The sender is configured to send an ARP broadcast every T seconds. An ARP broadcast packet is routed to every device on the network and is structured to say, "What MAC address has been assigned the IP address X.X.X.X?" The sender will send out this type of message for all 256 possible IP addresses on the network. In between the T seconds per broadcast, the sender will send direct ARP messages to every device in its device table. The number of direct messages between each broadcast can be configured. The sender also listens for zmq messages from the Forwarder that indicate there is a new device table. When this message is received, the sender updates its device table.

### Device Table Manager
The device table manager is responsible for keeping an up-to-date record of the devices on the network. The device table is just a list of device objects. The device object is composed of a device ID, a MAC address, an IP address, an alias, and a last-seen field. Each device object represents a device that got on to the network at any point. When the device table manager sees a new MAC address or if a MAC address has been assigned a new IP address, it sends to the Forwarder a a zmq message which contains the new device table.

### Database Interface
The database interface is responsible for getting information from and writing information to a database. Homenet uses a Google Sheet as its database. When it first runs, Homenet will create a new Google Sheet and all the worksheets it needs to log data. The database interface listens for messages over zmq that contain new device tables. When that message is received, the database interface sends the new information to the device_table worksheet to keep a back up of the device table. The database interface also listens for zmq messages that contain new arp packets. When these messages come in, the database interface writes the packet information to the arps worksheet.

### Message Forwarder
The Message Forwarder implements a zmq forwarder. It is the hub through which zmq messages are sent and consumed. Messages that route through the forwarder include new arp packets and new device table.
