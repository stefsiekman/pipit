import socket
import struct
import xstruct
import time

MULTICAST_GROUP = "239.255.1.1"
MULTICAST_PORT = 49707


def listen(timeout=3):
    # Setup socket to listen on X-Plane's multicast group
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((MULTICAST_GROUP, MULTICAST_PORT))
    mreq = struct.pack("=4sl", socket.inet_aton(MULTICAST_GROUP),
                       socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Try to find a beacon message for 5 seconds
    print(f"Listening for beacon for {timeout} sec...")
    start_time = time.time()
    sock.settimeout(timeout)

    try:
        (data, sender) = sock.recvfrom(1000)
    except OSError:
        return None

    print(f" ... {round(time.time() - start_time, 1)} sec")

    if data or sender:
        beacon_msg = decode_packet(data, sender)

        # Check the beacon message version number
        bv_major, bv_minor = beacon_msg["beacon_major_version"], \
                             beacon_msg["beacon_minor_version"]
        if bv_major != 1:
            print(f"Unknown BEACON version {bv_major}.{bv_minor}")
            return

        # Check that we're connected with the regular X-Plane
        if beacon_msg["application_id"] != 1:
            print("BEACON was from PlaneMaker")
            return
        if beacon_msg["role"] != 1:
            print("BEACON was not from master installation")
            return

        # Return the important information
        return beacon_msg["ip"], beacon_msg["port"], beacon_msg["hostname"]
    else:
        print("No beacon message was found")


def decode_packet(data, sender):
    # Make sure the header matches
    if data[:5] != b"BECN\x00":
        print("Non-BEACON message received")
        return

    # Decode the BEACON struct
    beacon_major, beacon_minor, app_id, version, role, port, hostname = \
        xstruct.decode(xstruct.BECN, data)

    # Convert the hostname to a string
    hostname = xstruct.decode_string(hostname)

    return {
        "ip": sender[0],
        "port": port,
        "hostname": hostname,
        "beacon_major_version": beacon_major,
        "beacon_minor_version": beacon_minor,
        "application_id": app_id,
        "version": version,
        "role": role,
    }
