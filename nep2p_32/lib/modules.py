import util.ip as i
import internal_gateway as igw
import external_gateway as egw
import scheduler as s
import batch_acknowledger as ba
import connection_pool as cp
import worker_pool as wp
#import recoder_pool as r
import bidict as b

ip = i.IP.Instance()
internal_gateway = igw.internal_gateway.Instance()
external_gateway = egw.external_gateway.Instance()
scheduler = s.scheduler.Instance()
batch_acknowledger = ba.batch_acknowledger.Instance()
connection_pool = cp.connection_pool.Instance()
worker_pool = wp.worker_pool.Instance()
#recoder_pool = r.recoder_pool.Instance()
bidict = b.bidict.Instance()
