import gp_concentrator.core.store as store
import datetime

sk = store.open("store")

start_time = datetime.datetime(2014, 10, 21, 19, 0, 0)
timeout = 0

while True:
    (sf, start_time) = sk.get_sfile_just_after(start_time)
    if start_time is None:
        break
    start_time += datetime.timedelta(seconds=1)
    node = sf.snapshot_list[0].node_list[0]
    if node.timeout is True:
        timeout += 1
    else:
        print (sf.snapshot_list[0].beat_time, ",", node.frequency)
