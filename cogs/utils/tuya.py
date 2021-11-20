import json

import tinytuya


def load_json_f(path):
    f = open(
        path,
    )
    data = json.load(f)
    f.close()
    return data


devices = load_json_f("tuya/devices.json")

####################
## DEVICE MANAGER ##
####################


def get_handle(device):
    if device["type"].find("bulb") != -1:
        d = tinytuya.BulbDevice(device["id"], device["ip"], device["key"])
    else:
        d = tinytuya.OutletDevice(device["id"], device["ip"], device["key"])
    if device["ver"] == "3.1":
        d.set_version(3.1)
    else:
        d.set_version(3.3)
    return d


def get_device(name):
    for dev in devices:
        if str(dev["name"]).find(name) == 0:
            return dev
    return None


## debug


def print_devices():
    print("Device list:")
    for dev in devices:
        print("   ", dev["name"])


#############
## CONTROL ##
#############

## ALL


def device_turn_on(device):
    d = get_handle(device)
    d.turn_on()


def device_turn_off(device):
    d = get_handle(device)
    d.turn_off()


def device_state(device):
    d = get_handle(device)
    data = d.status()
    print(data)


## Light Bulbs


def bulb_info(device):
    d = get_handle(device)
    data = d.status()
    print("Dictionary %r" % data)


def bulb_white(device):
    d = get_handle(device)
    d.set_white(255, 100)


def bulb_brightness(device, value=100):
    d = get_handle(device)
    d.set_brightness_percentage(value)


def bulb_color(device, r, g, b):
    d = get_handle(device)
    d.set_colour(r, g, b)


print_devices()
