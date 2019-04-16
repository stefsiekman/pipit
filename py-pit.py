import beacon
import refs
import threading
import queue


ref_queue = queue.Queue()


def handle_ref_change(ref, old_val, new_val):
    global ref_queue

    # Add the ref change to list to process
    ref_queue.put((ref, old_val, new_val))


if __name__ == "__main__":
    print("Trying to locate the X-Plane installation running")
    beacon_msg = beacon.listen()
    refs.setup_installation(beacon_msg)
    refs.request(5, ["laminar/B738/autopilot/hdg_sel_status"])
    refs.set_handler(handle_ref_change)

    ref_thread = threading.Thread(target=refs.listen)
    ref_thread.start()

    # Process incoming ref changes
    while True:
        ref, vold, vnew = ref_queue.get()
        print(f"Ref change {ref}:\t{vold} -> {vnew}")



