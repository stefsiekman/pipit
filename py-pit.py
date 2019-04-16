import beacon
import refs
import threading
import queue
import arduino
import time

TEST_REF = "laminar/B738/autopilot/hdg_sel_status"


ref_queue = queue.Queue()


def handle_ref_change(ref, old_val, new_val):
    global ref_queue

    # Add the ref change to list to process
    ref_queue.put((ref, old_val, new_val))


def fake_input():
    while True:
        print("Waiting for Arduino line print...")
        arduino.s.readline()
        refs.send_command("laminar/B738/autopilot/hdg_sel_press")


if __name__ == "__main__":
    print("Connecting to Arduino...")
    arduino.setup()

    print("Trying to locate the X-Plane installation running")
    beacon_msg = beacon.listen()
    refs.setup_installation(beacon_msg)
    refs.request(15, [TEST_REF])
    refs.set_handler(handle_ref_change)

    ref_thread = threading.Thread(target=refs.listen)
    ref_thread.start()

    input_thread = threading.Thread(target=fake_input)
    input_thread.start()

    # Process incoming ref changes
    while True:
        ref, vold, vnew = ref_queue.get()
        print(f"Ref change {ref}:\t{vold} -> {vnew}")
        arduino.set_led(vnew == 1)



