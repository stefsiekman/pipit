import beacon
import refs


def handle_ref_change(ref, old_val, new_val):
    print(f"{ref}\t{old_val} -> {new_val}")


if __name__ == "__main__":
    print("Trying to locate the X-Plane installation running")
    beacon_msg = beacon.listen()
    refs.setup_installation(beacon_msg)
    refs.request(5, ["laminar/B738/autopilot/hdg_sel_status"])
    refs.set_handler(handle_ref_change)

    while True:
        refs.receive()
