import socket
import time
import threading
import struct

REF_AIRSPEED = "sim/cockpit2/autopilot/airspeed_dial_kts_mach"
REF_DIGIT_8 = "laminar/B738/mcp/digit_8"
REF_DIGIT_A = "laminar/B738/mcp/digit_A"
CMD_AIRSPEED_UP = "sim/autopilot/airspeed_up"
CMD_AIRSPEED_DOWN = "sim/autopilot/airspeed_down"
REF_HEADING = "laminar/B738/autopilot/mcp_hdg_dial"
CMD_HEADING_UP = "sim/autopilot/heading_up"
CMD_HEADING_DOWN = "sim/autopilot/heading_down"

REF_ALTITUDE = "laminar/B738/autopilot/mcp_alt_dial"
CMD_ALTITUDE_UP = "sim/autopilot/altitude_up"
CMD_ALTITUDE_DOWN = "sim/autopilot/altitude_down"
REF_VERTICAL_SPEED = "sim/cockpit2/autopilot/vvi_dial_fpm"
CMD_VERTICAL_SPEED_UP = "sim/autopilot/vertical_speed_up"
CMD_VERTICAL_SPEED_DOWN = "sim/autopilot/vertical_speed_down"

REF_COURSE_CPT = "sim/cockpit2/radios/actuators/nav1_obs_deg_mag_pilot"
CMD_COURSE_CPT_UP = "laminar/B738/autopilot/course_pilot_up"
CMD_COURSE_CPT_DOWN = "laminar/B738/autopilot/course_pilot_dn"
REF_COURSE_FO = "sim/cockpit2/radios/actuators/nav1_obs_deg_mag_copilot"
CMD_COURSE_FO_UP = "laminar/B738/autopilot/course_copilot_up"
CMD_COURSE_FO_DOWN = "laminar/B738/autopilot/course_copilot_dn"

REF_NAV_ACT = "sim/cockpit/radios/nav1_freq_hz"
REF_NAV_STDBY = "sim/cockpit/radios/nav1_stdby_freq_hz"
CMD_NAV_FLIP = "sim/radios/nav1_standy_flip"
CMD_NAV_COARSE_UP = "sim/radios/stby_nav1_coarse_up"
CMD_NAV_COARSE_DOWN = "sim/radios/stby_nav1_coarse_down"
CMD_NAV_FINE_UP = "sim/radios/stby_nav1_fine_up"
CMD_NAV_FINE_DOWN = "sim/radios/stby_nav1_fine_down"

REF_COM_ACT = "sim/cockpit/radios/com1_freq_hz"
REF_COM_STDBY = "sim/cockpit/radios/com1_stdby_freq_hz"
CMD_COM_FLIP = "sim/radios/com1_standy_flip"
CMD_COM_COARSE_UP = "sim/radios/stby_com1_coarse_up"
CMD_COM_COARSE_DOWN = "sim/radios/stby_com1_coarse_down"
CMD_COM_FINE_UP = "sim/radios/stby_com1_fine_up"
CMD_COM_FINE_DOWN = "sim/radios/stby_com1_fine_down"

REF_STATUS_ALT_HLD = "laminar/B738/autopilot/alt_hld_status"
REF_STATUS_VS = "laminar/B738/autopilot/vs_status"

REF_STATUS_VNAV = "laminar/B738/autopilot/vnav_status1"
REF_STATUS_LNAV = "laminar/B738/autopilot/lnav_status"
CMD_PRESS_LNAV = "laminar/B738/autopilot/lnav_press"
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


def installation_is_setup():
    global beacon
    return beacon is not None


def start_thread():
    global thread

    thread = threading.Thread(target=listen)
    thread.start()


def stop_connection():
    global running, registered_refs, thread

    print("Stopping connection...")

    running = False

    # Stop requesting the refs
    request(0, [registered_refs[index][0] for index in registered_refs.keys()])

    thread.join()


def send(ref, value):
    global sock

    packet = struct.pack("<5sf500s", b"DREF\x00", value, ref.encode())
    sock.sendto(packet, (beacon[0], beacon[1]))


last_command = None
last_command_time = time.time()


def send_command(cmd, fast_repeat=False):
    global sock, last_command, last_command_time

    now = time.time()
    should_repeat = fast_repeat and last_command == cmd and \
                    now - last_command_time < 0.050
    last_command_time = now
    last_command = cmd

    packet = b"CMND\x00" + cmd.encode() + b"\x00"
    for _ in range(5 if should_repeat else 1):
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


def current_value(ref):
    for saved_ref, value in registered_refs.values():
        if saved_ref == ref:
            return value
