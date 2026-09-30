"""Request-local timings. Parent durations include children; parallel rows overlap."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from threading import Lock
from time import perf_counter

_current = ContextVar('verification_trace', default=None)
_parent = ContextVar('verification_span', default=None)

class Trace:
    def __init__(self):
        self.start = perf_counter()
        self.rows = []
        self.lock = Lock()
        self.next_id = 0

    @contextmanager
    def span(self, stage, scope='', **meta):
        start = perf_counter()
        with self.lock:
            self.next_id += 1
            row = dict(id=self.next_id, parent_id=_parent.get(), stage=stage,
                       scope=scope, start_ms=(start-self.start)*1000, outcome='completed', **meta)
            self.rows.append(row)
        token = _parent.set(row['id'])
        try:
            yield row
        except BaseException as exc:
            row.update(outcome='error', error_type=type(exc).__name__)
            raise
        finally:
            row['elapsed_ms'] = (perf_counter()-start)*1000
            _parent.reset(token)

    def report(self):
        with self.lock:
            return dict(total_ms=round((perf_counter()-self.start)*1000, 3),
                        rows=[{k:round(v,3) if isinstance(v,float) else v for k,v in r.items()}
                              for r in self.rows],
                        note='Parent rows include child times; parallel rows overlap. Do not sum all rows.')

@contextmanager
def activate(trace):
    token = _current.set(trace)
    try:
        yield
    finally:
        _current.reset(token)

def current_trace():
    return _current.get()

@contextmanager
def span(stage, scope='', **meta):
    trace = _current.get()
    if trace is None:
        yield {}
    else:
        with trace.span(stage, scope, **meta) as row:
            yield row

def timed(stage, scope_arg=None):
    def decorate(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            scope = ''
            if scope_arg is not None and len(args)>scope_arg:
                value = args[scope_arg]
                scope = str(value.get('id') or value.get('issuer') or '') if isinstance(value,dict) else str(value)
            with span(stage, scope):
                return func(*args, **kwargs)
        return wrapped
    return decorate

def profiled(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        enabled = kwargs.pop('collect_timings', True)
        if not enabled:
            return func(*args, **kwargs)
        trace = _current.get() or Trace()
        with activate(trace), span('verification_total'):
            report = func(*args, **kwargs)
        return dict(report, timings=trace.report())
    return wrapped
