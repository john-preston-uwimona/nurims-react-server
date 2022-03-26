import psycopg2
from psycopg2.extras import DictCursor
from datetime import date, datetime, timedelta


def calculate_availability(cur):
    availability = 0
    days = 0
    perday = []
    row = cur.fetchone()
    while row is not None:
        # each day should have a total of 1440 as the ping interval is 1 minute
        perday.append({"value": float(row['hk_numeric_value']) / 1440.0, "day": str(row['hk_ts'])})
        availability += float(row['hk_numeric_value'])
        days += 1.0
        row = cur.fetchone()

    # return 0 if days == 0 else availability / (1440.0 * days)
    return {
        "aggregate": 0 if days == 0 else availability / (1440.0 * days),
        "perday": perday
    }


def update_availability(pg, log, request):
    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        log.trace("searching for housekeeping availability records for {} on date {}"
                  .format(request["client_id"], str(date.today())))
        cur.execute("SELECT hk_numeric_value FROM housekeeping where client_id = %s and hk_key = %s and hk_ts = %s",
                    (request["client_id"], "availability", date.today(),))
        log.trace("found {} records".format(cur.rowcount))
        row = cur.fetchone()

        if row is None:
            log.trace("creating initial availability record for {} on {}"
                      .format(request["client_id"], str(date.today())))
            cur.execute("INSERT INTO housekeeping(client_id,hk_key,hk_numeric_value,hk_ts) values (%s,%s,%s,%s)",
                        (request["client_id"], "availability", 1, date.today(),))
        else:
            log.trace("updating housekeeping availability record for {} on {}"
                      .format(request["client_id"], str(date.today())))
            cur.execute(
                "UPDATE housekeeping SET hk_numeric_value = %s WHERE client_id = %s and hk_key = %s and hk_ts = %s",
                (int(row["hk_numeric_value"]) + 1, request["client_id"], "availability", date.today()), )

        request.update({
            "data": {
                "message": "",
                "status": 0
            }})

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        log.error(error)
    finally:
        if cur is not None:
            cur.close()


def get_availability(pg, log, request):
    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        log.trace("searching for housekeeping availability records for {}".format(request["client_id"]))
        cur.execute("SELECT hk_numeric_value FROM housekeeping where client_id = %s and hk_key = %s",
                    (request["client_id"], "availability",))
        log.trace("found {} records".format(cur.rowcount))
        row = cur.fetchone()

        if row is None:
            request.update({
                "data": {
                    "availability": 0,
                    "message": "",
                    "status": 0
                }})
        else:
            today = date.today()
            today_less_10 = today - timedelta(days=9)
            log.trace("retrieving availability record for client {} between {} and {}"
                      .format(request["client_id"], str(today_less_10), str(today)))
            cur.execute("""SELECT hk_ts, hk_numeric_value FROM housekeeping WHERE client_id = %s AND
                           hk_key = %s AND hk_ts BETWEEN %s AND %s ORDER BY hk_ts""",
                        (request["client_id"], "availability", today_less_10, today))
            request.update({
                "data": {
                    "availability": calculate_availability(cur),
                    "message": "",
                    "status": 0
                }})

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        log.error(error)
    finally:
        if cur is not None:
            cur.close()
