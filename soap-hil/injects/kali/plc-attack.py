import snap7
import sys
import ctypes
from time import sleep

from snap7.client import Client
from snap7.types import Areas

__DEBUG__ = True


def __dbg(str):
    if __DEBUG__:
        print(str)


def write_analog(client: Client, area: Areas, off: int, bts: int, val: int):
    dbn = 0
    ws = val.to_bytes(bts, 'big')
    __dbg(
        f"[write_analog]\tIO: {'I' if area==Areas.PE else 'O'}\toff: {off}\tbts: {bts}\tval: {val}"
    )
    return client.write_area(area, dbn, off, ws)


def read_analog(client: Client, area: Areas, off: int, bts: int):
    dbn = 0
    byts = client.read_area(area, dbn, off, bts)
    val = int.from_bytes(byts, 'big')
    __dbg(
        f"[read_analog]\tIO: {'I' if area==Areas.PE else 'O'}\toff: {off}\tbts: {bts}\tval: {val}"
    )
    return val


def read_digital_byte(client: Client, area: Areas, off: int):
    dbn = 0
    bts = 1
    return client.read_area(area, dbn, off, bts)[0]


def read_digital(client: Client, area: Areas, off: int, bit: int):
    byt = read_digital_byte(client, area, off)
    r = (byt & (1 << bit)) >> bit
    __dbg(
        f"[read_digital]\tIO: {'I' if area==Areas.PE else 'O'}\toff: {off}\tbit: {bit}\tval: {r:01b}\t"
    )
    return r


def write_digital(client: Client, area: Areas, off: int, bit: int, val: int):
    dbn = 0
    r = read_digital_byte(client, area, off)
    tw = (r & ~(1 << bit)) | (val << bit)
    w = tw.to_bytes(1, 'big')
    __dbg(
        f"[write_digital]\tIO: {'I' if area==Areas.PE else 'O'}\toff: {off}\tbit: {bit}\tval: {val:01b}\t\twrt: {tw:02x}"
    )
    return client.write_area(area, dbn, off, w)


def write_mw_val(client, mw_val: int):
    if mw_val > 100 or mw_val < 0:
        raise ValueError("mw_val must be between 0 and 100")
    area = Areas.PA
    off = 96
    sh = 100
    rh = 13429
    mw_raw = int(mw_val * (rh / sh))
    w = mw_raw.to_bytes(2, 'big')
    return write_analog(client, area, off, 2, mw_raw)


def read_mw_val(client):
    area = Areas.PA
    off = 96
    sh = 100
    rh = 13429
    mw_raw = read_analog(client, area, off, 2)
    return int(mw_raw * (sh / rh))


def write_rly(client: Client, val: bool):
    area = Areas.PA
    off = 1
    bit = 0
    return write_digital(client, area, off, bit, val)


def read_rly(client: Client):
    area = Areas.PA
    off = 1
    bit = 0
    return read_digital(client, area, off, bit)


def main(sdly, rpts):
    ss = 1
    sl = 4
    ssl = sdly

    sleep(ssl)

    client = Client()
    client.connect("10.117.4.110", 0, 0)

    for _ in range(0, rpts):
        write_rly(client, False)
        sleep(ss)
        write_mw_val(client, 50)
        sleep(ss)
        write_rly(client, True)

        print(f"mw_val: {read_mw_val(client)}")

        sleep(sl)

        write_rly(client, False)
        sleep(ss)
        write_mw_val(client, 100)
        sleep(ss)
        write_rly(client, True)
        print(f"mw_val: {read_mw_val(client)}")

    client.disconnect()


def usage(argv0):
    return f"{argv0}: <STARTUP_DELAY : int> <REPEATS : int>"


def parse_args(args):
    if len(args) != 3:
        print(usage(args[0]), file=sys.stderr)
        exit(1)
    return (int(args[1]), int(args[2]))


if __name__ == "__main__":
    import sys
    sdly, rpts = parse_args(sys.argv)

    main(sdly, rpts)
