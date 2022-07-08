import sys
import struct
import base64
import json

"""
Generate CSV file from JSON data. First argument is the JSON file, second is the output file.
"""


def decode_channel(channel_data, fmt):
    """
    Decode single channel from base64 to numbers

    Args:
        channel_data (str): base64 channel data
        fmt (str): format for `struct` package
    """
    if isinstance(channel_data, str):
        channel_data = channel_data.encode('utf-8')
    b64_decoded = base64.decodebytes(channel_data)
    try:
        return struct.unpack(fmt, b64_decoded)
    except:
        return "BUSTED"


def decode_channels(channels, fmt):
    """
    Update the r_dict in-place (without generating a copy) to encode the data lists as base64 packed binary strings.

    Args:
        channels (dict): Channel waveforms, packed as base64.
        fmt (str): struct format for channel data.
    Returns:
        dict: channel waveform as tuples of floats.
    """
    ret = {}

    for ch in channels:
        try:
            ret[ch] = decode_channel(channels[ch], fmt)
        except:
            ret[ch] = "BUSTED"

    return ret


def unpack_rit_json(json_as_bytes):
    """
    Unpack JSON data for clinical data for RIT
    Args:
        json_as_bytes: (bytes) input JSON data.
    Returns:
        dict: Dictionary holding clinical data.
    """
    rit_data = json.loads(json_as_bytes)
    rit_data['channels'] = decode_channels(rit_data['channels'], rit_data['channel_format'])
    return rit_data


def read_json(filename):
    with open(filename, "rb") as f:
        return unpack_rit_json(f.read())


rit_datas = read_json(sys.argv[1])

with open(sys.argv[2], "w") as file:
    file.write("10 leads sampled @1.0ms, 1,\n")
    i = 0
    while i < len(rit_datas["channels"]["ecg"]):
        s = str(i)
        for x in ["ecg", "ppg_ir", "ppg_red", "weight_br", "weight_fr", "weight_bl", "bcg_br", "bcg_fr",
                  "bcg_bl", "bcg_fl"]:
            s += "," + str(rit_datas["channels"][x][i])
        file.write(s + ",\n")
        i += 1
