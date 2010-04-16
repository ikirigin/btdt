#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
import math
import random
import time
import pickle
import webbrowser
from datetime import datetime, timedelta

def find_p(x, sigma):
    return (1.0 / (sigma * math.sqrt(2*math.pi))) * math.exp((-1.0 * (x-1)*(x-1)) / (2.0 * sigma * sigma))

def exp_dist_cdf(x, _lambda = 1):
    return 1 - math.exp( -x * _lambda )
    
def print_duration(d):
    return d.seconds + (d.microseconds/ 1000000.0)

def mean_call(foo):
    return sum([foo() for x in range(100000)]) / 100000.0

def should_drop(time_passed):
    d = {}
    d['input'] = time_passed
    d['time_passed'] = time_passed.seconds + (time_passed.microseconds / 1000000.0)
    d['probability'] = exp_dist_cdf(d['time_passed'])
    d['random'] = random.random()
    d['result'] =     d['random'] < d['probability']
    print d
    return d['result']

def make_it_rain(duration):
    drop_times = []
    now = last_drop = start_time = datetime.now()
    end_time = start_time + duration
    while now < end_time:
        start_loop = datetime.now()
        if should_drop(now - last_drop):
            drop_times.append(now)
            print 'dropped in ', print_duration(now - last_drop), 'seconds'
            last_drop = now
        end_loop = datetime.now()
        print 'this loop run took:', end_loop - start_loop
        now = datetime.now()
    return drop_times
        
# trying to estimate the probability of 2 within 50ms. Failed.
def get_sample_range_pairs():
    return [[x, 0.05-x] for x in map(lambda x: x / 100000.0, range(1, 5000))]

def sample_range():
    return sum( map(lambda x: exp_dist_cdf(x[0])*exp_dist_cdf(x[1]), get_sample_range_pairs()) )

# simulate the poisson process
def get_internval(_lambda = 1):
    return -math.log(random.random()) / _lambda 

def list_derivative( arr ):
    return [arr[i] - arr[i-1] for i in range(1,len(arr))]

def get_a_mess_o_raindrops(num):
    return [get_internval() for x in xrange(num)]


'''
>>> estimate_interval_likelihood(0.05, 1000)
0.058000000000000003
>>> estimate_interval_likelihood(0.05, 10000)
0.049000000000000002
>>> estimate_interval_likelihood(0.05, 100000)
0.048149999999999998
>>> estimate_interval_likelihood(0.05, 1000000)
0.048763000000000001
>>> estimate_interval_likelihood(0.05, 10000000)
0.048664300000000001
>>> estimate_interval_likelihood(0.05, 100000000)
0.048763689999999998

>>> exp_dist_cdf(0.05)
0.048770575499285984


'''
def estimate_interval_likelihood(interval=0.05, count=100):
    total_num = 0 
    observed_num = 0
    # avoided list comprehensions because a high count is too memory intensive
    for x in xrange(count):
        total_num += 1
        if get_internval() <= interval:
            observed_num += 1
    return observed_num / float(total_num)

def estimate_double_fire(p=0.5, interval=0.05, count=100):
    waits = []
    intervals = [get_internval() for x in range(count)]
    for i in range(1,count):
        if intervals[i-1] < interval:
            waits.append( intervals[i] )
    # sorting the waits and returning the on P% in should estimate the time
    waits.sort()
    return waits[int(p*len(waits))]

def pickle_raindrops():
    f = open('raindrops.txt', 'r').read()
    times = map(float, f.split())
    p = open('raindrop.pkl', 'wb')
    pickle.dump(times, p)
    p.close()

def gen_goog_histogram(values, num_bins=100):
    # normalize, multiply by 1000, and bucket
    max_ = max(values)
    normalized = map(lambda x: int(num_bins * x / max_), values)
    buckets = {}
    for n in normalized:
        buckets[n] = buckets.get(n, 0) + 1
    ordered_bins = [buckets.get(x, 0) for x in range(0,num_bins+1)]
    # normalize 0...100
    max_ = max(ordered_bins)
    ordered_bins = map(lambda x: 100*x/max_, ordered_bins)
    u = 'http://chart.apis.google.com/chart?cht=lc&chs=1000x300&chd=t:' + ','.join(map(str,ordered_bins))
    webbrowser.open(u)

def gen_goog_timeseries(values, limit=500, offset=0):
    vals = values[offset:offset+limit]
    # normalize
    max_ = max(vals)
    normalized_vals = map(lambda x: int(100 * x / max_), vals)
    # only consider up to limit points
    u = 'http://chart.apis.google.com/chart?cht=lc&chs=500x500&chd=t:' + ','.join(map(str,normalized_vals))
    webbrowser.open(u)

def gen_integer_buckets(times, count=800, offset=0):
    ints = {}
    for t in times:
        i = int(t)
        ints[i] = ints.get(i,0) + 1
    max_int = int(max(times))
    min_int = int(min(times))
    all_ints = []
    for x in range(min_int, max_int+1):
        all_ints.append(ints.get(x,0))
    # cut off by the count / offset
    max_count = max(all_ints)
    normalized_ints = map(lambda x: int(100 * x / max_count), all_ints)
    normalized_ints = normalized_ints[offset:offset+count]
    u = 'http://chart.apis.google.com/chart?cht=lc&chs=1000x300&chd=t:' + ','.join(map(str,normalized_ints))
    webbrowser.open(u)        

def gen_goog_exp_cdf(values, num_buckets=500):
    max_ = max(values)
    bucket_step = max_ / num_buckets
    bucket_thresholds = []
    last = 0
    for x in range(num_buckets):
        next = last + bucket_step
        bucket_thresholds.append(next)
        last = next
    values.sort()
    bucket_num = 0
    buckets = [0] * num_buckets
    for v in values:
        if v >= bucket_thresholds[bucket_num]:
            bucket_num += 1
        buckets[bucket_num] += 1
    # now find the cumulative total in each bucket
    running_totals = [buckets[0]]
    for i,b in enumerate(buckets[1:]):
        running_totals.append( running_totals[i] + b )
    # now normalize to get a cdf
    count = float(len(values))
    cdf = map(lambda x: x / count, running_totals)
    plottable = map(lambda x: int(100*x), cdf)
    u = 'http://chart.apis.google.com/chart?cht=lc&chs=500x500&chd=t:' + ','.join(map(str,plottable))
    webbrowser.open(u)
    return cdf
    

def analyze_raindrops():
    # load the raindrop times
    times = pickle.load(open('raindrops.pkl','rb'))
    # get the time differences (i goes from 0...len-1, and the time is from times[1]...times[len])
    intervals = [ time - times[i] for i, time in enumerate(times[1:]) ]
    interval_mean = sum(intervals) / float(len(intervals))
    interval_median = intervals[int(len(intervals)/2)]

if __name__ == '__main__':
    drop_times = make_it_rain(timedelta(seconds=2))
    print drop_times
    print '\n there were this many:', len(drop_times)