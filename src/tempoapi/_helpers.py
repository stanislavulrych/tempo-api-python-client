from datetime import date, datetime, time


def resolve_date(value: str | date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(value, r"%Y-%m-%d").date()


def resolve_time(value: str) -> time:
    _v = strip_hrs(value)
    _h = 0
    _m = 0
    _s = 0
    if "pm" in _v:
        _v = _v.replace("pm", "")
        _h = int(_v.split(":")[0])
        if _h < 12:
            _h = _h + 12
        elif _h == 12:
            _h = 0
    else:
        _h = int(_v.split(":")[0])
    if _h > 99:
        _h = int(_h / 100)
    if _v.count(":") == 2:
        _m = int(_v.split(":")[1])
        _s = int(_v.split(":")[2])
    elif _v.count(":") == 1:
        _m = int(_v.split(":")[1])
    value = f"{_h:02d}:{_m:02d}:{_s:02d}"
    return datetime.strptime(value, r"%H:%M:%S").time()


def strip_hrs(value: str) -> str:
    _hrs = ["am", "uhr", "hrs", "hours", "hour"]
    retval = value.lower().replace(" ", "").replace(".", ":")
    for i in _hrs:
        retval = retval.replace(i, "")
    return retval.strip()
