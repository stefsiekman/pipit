import socket
import threading
import struct

REF_AIRSPEED = "sim/cockpit2/autopilot/airspeed_dial_kts_mach"
CMD_AIRSPEED_UP = "sim/autopilot/airspeed_up"
CMD_AIRSPEED_DOWN = "sim/autopilot/airspeed_down"
REF_HEADING = "laminar/B738/autopilot/mcp_hdg_dial"
CMD_HEADING_UP = "sim/autopilot/heading_up"
CMD_HEADING_DOWN = "sim/autopilot/heading_down"
REF_STATUS_LNAV = "laminar/B738/autopilot/lnav_status"
CMD_PRESS_LNAV = "laminar/B738/autopilot/lnav_press"
REF_STATUS_VNAV = "laminar/B738/autopilot/vnav_status"
CMD_PRESS_VNAV = "laminar/B738/autopilot/vnav_press"
REF_STATUS_HDG_SEL = "laminar/B738/autopilot/hdg_sel_status"
CMD_PRESS_HDG_SEL = "laminar/B738/autopilot/hdg_sel_press"

sock = None
registered_refs = {}
next_ref_index = 1
beacon = None
handler = None
running = False
thread = None


def setup_installation(beacon_info):
    global beacon, sock, running

    print(f"Setting up REFS communication for {beacon_info[2]}")
    beacon = beacon_info
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    running = True


def start_thread():
    global thread

    thread = threading.Thread(target=listen)
    thread.start()


def stop_connection():
    global running, registered_refs, thread

    running = False

    # Stop requesting the refs
    request(0, [registered_refs[index][0] for index in registered_refs.keys()])

    thread.join()


def send(ref, value):
    global sock

    packet = struct.pack("<5sf500s", b"DREF\x00", value, ref.encode())
    sock.sendto(packet, (beacon[0], beacon[1]))


def send_command(cmd):
    global sock

    packet = b"CMND\x00" + cmd.encode() + b"\x00"
    sock.sendto(packet, (beacon[0], beacon[1]))


def request(freq, refs):
    global next_ref_index, sock

    if len(refs) > 140:
        print("WARNING: requesting more than 140 refs in one go")

    for ref in refs:
        # Create the packet for the RREF
        if freq:
            registered_refs[next_ref_index] = ref, None
            next_ref_index += 1
        send_index = next_ref_index - 1 if freq else 0
        packet = struct.pack("<5sii400s", b"RREF\x00", freq, send_index,
                             ref.encode())

        # Send the request
        sock.sendto(packet, (beacon[0], beacon[1]))


def request_all():
    request(15, [ref for name, ref in globals().items()
                 if name.startswith("REF_")])


def set_handler(new_handler):
    global handler

    handler = new_handler


def listen():
    global running

    while running:
        receive()


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
