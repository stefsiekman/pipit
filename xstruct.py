import struct

# struct becn_struct
# {
# 	uchar beacon_major_version;	    // 1 at the time of X-Plane 10.40
# 	uchar beacon_minor_version;	    // 1 at the time of X-Plane 10.40
# 	xint application_host_id;		// 1 for X-Plane, 2 for PlaneMaker
# 	xint version_number;			// 104103 for X-Plane 10.41r3
# 	uint role;						// 1 for master, 2 for extern visual, 3 for IOS
# 	ushort port;					// port number X-Plane is listening on, 49000 by default
# 	xchr	computer_name[500];		// the hostname of the computer, e.g. “Joe’s Macbook”
# };
BECN = "<BBiiIH500s"


def decode(format, packet):
    # Remove the header
    data = packet[5:]

    # See if padding of the data is required
    length = struct.calcsize(format)
    if length - len(data) > 0:
        data = struct.pack(f"{length}s", data)

    # Decode the actual struct
    return struct.unpack(format, data)


def decode_string(byte_string):
    # Find the null terminator
    null_index = len(byte_string) - 1
    for index, byte in enumerate(byte_string):
        if byte == 0:
            null_index = index
            break

    # Convert the terminated string using UTF-8
    return byte_string[0:null_index].decode("utf-8")

