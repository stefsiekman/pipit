import socket
import struct

sock = None
registered_refs = {}
next_ref_index = 1
beacon = None
handler = None


def setup_installation(beacon_info):
    global beacon, sock

    print(f"Setting up REFS communication for {beacon_info[2]}")
    beacon = beacon_info
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def request(freq, refs):
    global next_ref_index, sock

    if len(refs) > 140:
        print("WARNING: requesting more than 140 refs in one go")

    for ref in refs:
        # Create the packet for the RREF
        registered_refs[next_ref_index] = ref, None
        packet = struct.pack("<5sii400s", b"RREF\x00", freq, next_ref_index,
                             ref.encode())
        next_ref_index += 1

        # Send the request
        sock.sendto(packet, (beacon[0], beacon[1]))


def set_handler(new_handler):
    global handler

    handler = new_handler


def receive():
    global sock, registered_refs

    data, address = sock.recvfrom(1500)

    # Check the header
    if data[:5] != b"RREF,":
        print("Received non-RREF response")
        print(data)
        return

    # Decode the message
    values = data[5:]
    num_values = len(values) // 8
    for i in range(num_values):
        value_struct = values[i * 8:(i + 1) * 8]
        index, value = struct.unpack("<if", value_struct)

        # Update the ref value
        old_value = registered_refs[index][1]
        if old_value != value:
            ref = registered_refs[index][0]
            registered_refs[index] = ref, value
            if handler:
                handler(ref, old_value, value)
