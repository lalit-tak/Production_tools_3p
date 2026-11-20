import datetime
import json
import logging
import os
import threading

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json


DB_CONFIG = {
    "host": "PUT_YOUR_EMS_HOST_HERE",
    "port": "PUT_YOUR_EMS_PORT_HERE",
    "database": "PUT_YOUR_EMS_DATABASE_HERE",
    "user": "PUT_YOUR_EMS_USER_HERE",
    "password": "PUT_YOUR_EMS_PASSWORD_HERE",
}
TABLE_SCHEMA = "PUT_YOUR_EMS_SCHEMA_HERE"

DB_CONFIG_ATHENA = {
    "host": "PUT_YOUR_ATHENA_HOST_HERE",
    "port": "PUT_YOUR_ATHENA_PORT_HERE",
    "database": "PUT_YOUR_ATHENA_DATABASE_HERE",
    "user": "PUT_YOUR_ATHENA_USER_HERE",
    "password": "PUT_YOUR_ATHENA_PASSWORD_HERE",
}
TABLE_SCHEMA_ATHENA = "PUT_YOUR_ATHENA_SCHEMA_HERE"

_conn = None
_athena_con = None
# Guards _conn/_athena_con so concurrent per-COM-port threads can't each
# see "no connection yet" at the same time and all open their own
# psycopg2.connect() simultaneously (that pile-up is what was causing the
# "connection to server ... timeout expired" bursts with many ports).
_conn_lock = threading.Lock()

COLUMN_MAPPING_CALIB = {
    "MAC_ADDR": "mac_addr",
    "Index": "index",
    "Date_time": "date_time",
    "Meter_IP_Address": "meter_ip_address",
    "Meter_PCB_Serial_No": "meter_pcb_serial_no",
    "CalibSign": "calib_sign",
    "FrequencyCoeff_min": "frequency_coeff_min",
    "FrequencyCoeff_max": "frequency_coeff_max",
    "FrequencyCoeff": "frequency_coeff",
    "VCoeff_min": "v_coeff_min",
    "VCoeff_max": "v_coeff_max",
    "VCoeff": "v_coeff",
    "ICoeff[0]_min": "i_coeff_0_min",
    "ICoeff[0]_max": "i_coeff_0_max",
    "ICoeff[0]": "i_coeff_0",
    "ICoeff[1]_min": "i_coeff_1_min",
    "ICoeff[1]_max": "i_coeff_1_max",
    "ICoeff[1]": "i_coeff_1",
    "ActPowerCoeff[0]_min": "act_power_coeff_0_min",
    "ActPowerCoeff[0]_max": "act_power_coeff_0_max",
    "ActPowerCoeff[0]": "act_power_coeff_0",
    "ActPowerCoeff[1]_min": "act_power_coeff_1_min",
    "ActPowerCoeff[1]_max": "act_power_coeff_1_max",
    "ActPowerCoeff[1]": "act_power_coeff_1",
    "PhAngle[0]_min": "ph_angle_0_min",
    "PhAngle[0]_max": "ph_angle_0_max",
    "PhAngle[0]": "ph_angle_0",
    "PhAngle[1]_min": "ph_angle_1_min",
    "PhAngle[1]_max": "ph_angle_1_max",
    "PhAngle[1]": "ph_angle_1",
    "Overall_Result": "overall_result",
    "Get_Meter_Address": "get_meter_address",
    "Get_Meter_PCB_No": "get_meter_pcb_no",
    "Calibration_Unlock": "calibration_unlock",
    "Phase_calibration": "phase_calibration",
    "Neutral_calibration": "neutral_calibration",
    "Get_1p_calib_cofficient": "get_1p_calib_coefficient",
    "CalibSign_Status": "calib_sign_status",
}

_NUMERIC_COLUMN_TYPES = {
    "double precision", "real", "numeric", "decimal",
    "integer", "bigint", "smallint",
}
_NON_NUMERIC_PLACEHOLDERS = {"fail", "na", "n/a", "nan", ""}


def start_connection(conn_type):
    global _conn
    global _athena_con

    with _conn_lock:
        try:
            if conn_type == 'ems':
                # Re-check inside the lock: another thread may have already
                # connected while this thread was waiting for the lock.
                if _conn and not _conn.closed:
                    return _conn
                _conn = psycopg2.connect(connect_timeout=5, **DB_CONFIG)
                _conn.autocommit = False
                logging.info("EMS Database connection started")
                return _conn
            else:
                if _athena_con and not _athena_con.closed:
                    return _athena_con
                _athena_con = psycopg2.connect(connect_timeout=5, **DB_CONFIG_ATHENA)
                _athena_con.autocommit = False
                print(f"Athena Database connection started")
                logging.info("Athena Database connection started")
                return _athena_con
        except Exception as exc:
            _conn = None
            _athena_con = None
            logging.error("Database connection failed: %s", exc)
            return None

def close_connection():
    global _conn
    global _athena_con
    with _conn_lock:
        if _conn and not _conn.closed:
            try:
                _conn.close()
                logging.info("EMS Database connection closed")
            except Exception as exc:
                logging.error("Error while closing EMS database connection: %s", exc)

        if _athena_con and not _athena_con.closed:
            try:
                _athena_con.close()
                logging.info("Athena Database connection closed")
            except Exception as exc:
                logging.error("Error while closing Athena database connection: %s", exc)
        _conn = None
        _athena_con = None

def _get_connection(conn_type = 'ems'):
    if conn_type == 'ems':
        if _conn is None or _conn.closed:
            return start_connection(conn_type)
        return _conn
    else:
        if _athena_con is None or _athena_con.closed:
            return start_connection(conn_type)
        return _athena_con
    
def _table_columns(cursor, table_name, schema):
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """,
        (schema, table_name),
    )
    
    return [row[0] for row in cursor.fetchall()]

def _table_column_types(cursor, table_name):
    """Map column_name -> data_type (e.g. 'double precision', 'text') for this table."""
    cursor.execute(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        """,
        (TABLE_SCHEMA, table_name),
    )
    return {row[0]: row[1] for row in cursor.fetchall()}

def _is_nan(value):
    # NaN is the only value in Python that is not equal to itself
    try:
        return value != value
    except Exception:
        return False

def _coerce_value(value, col, column_types):
    """Make a value safe to insert into `col` given its real DB type.

    The calibration scripts write placeholder strings like 'Fail'/'NA' into
    what are numeric columns (FrequencyCoeff, VCoeff, etc.) whenever a test
    step didn't succeed. Postgres can't cast those strings to
    double precision, so we turn them (and pandas NaN) into NULL instead,
    while leaving genuinely numeric and non-numeric-column values untouched.
    """
    if _is_nan(value):
        return None
    if column_types.get(col) not in _NUMERIC_COLUMN_TYPES:
        return value
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in _NON_NUMERIC_PLACEHOLDERS:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def upload_dataframe(df_frame, meter_type):
    mapping = COLUMN_MAPPING_CALIB
    if 'better' in meter_type:
        TABLE_NAME = "BETTER1P_CALIB"
    else:
        TABLE_NAME = "GARUD1P_CALIB"
    missing_cols = [col for col in mapping if col not in df_frame.columns]
    if missing_cols:
        error_msg = f"DataFrame is missing expected columns: {missing_cols}"
        logging.error(error_msg)
        return False, error_msg

    df_renamed = df_frame.rename(columns=mapping)
    df_renamed["date"] = datetime.date.today()

    conn = _get_connection('ems')
    if conn is None:
        error_msg = "Database connection not available"
        logging.error(error_msg)
        return False, error_msg
    try:
        with conn.cursor() as cursor:
            db_columns = _table_columns(cursor, TABLE_NAME, TABLE_SCHEMA)
            db_columns_lower = {c.lower(): c for c in db_columns}  # map lower -> real name
            db_column_types = _table_column_types(cursor, TABLE_NAME)

            insert_columns = [col for col in mapping.values() if col in db_columns]

            if "date" in db_columns_lower and "date" not in insert_columns:
                insert_columns.append(db_columns_lower["date"])  # use real column name/casing

            if not insert_columns:
                error_msg = (
                    f'No matching mapped columns found in "{TABLE_SCHEMA}"."{TABLE_NAME}" '
                    f"for dataframe upload"
                )
                logging.error(error_msg)
                return False, error_msg

            query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
                sql.Identifier(TABLE_SCHEMA),
                sql.Identifier(TABLE_NAME),
                sql.SQL(", ").join(map(sql.Identifier, insert_columns)),
                sql.SQL(", ").join(sql.Placeholder() * len(insert_columns)),
            )

            for _, row in df_renamed.iterrows():
                # values = [
                #     Json(row[col]) if isinstance(row[col], (list, dict)) else row.get(col, None) if col != db_columns_lower.get("date") else row["date"]
                #     for col in insert_columns
                # ]
                values = []
                for col in insert_columns:
                    if col == db_columns_lower.get("date"):
                        values.append(row["date"])
                        continue
                    raw_value = row.get(col, None)
                    if isinstance(raw_value, (list, dict)):
                        values.append(Json(raw_value))
                    else:
                        values.append(_coerce_value(raw_value, col, db_column_types))
                cursor.execute(query, values)

        conn.commit()
        logging.info("Uploaded %d rows to %s.%s table", len(df_renamed), TABLE_SCHEMA, TABLE_NAME)
        return True, None

    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        error_msg = str(exc)
        logging.error("Dataframe upload failed: %s", error_msg)
        return False, error_msg

def fetch_by_pcb_serial(pcb_serial_no, meter_type=None):
    """
    Fetch calibration rows for a given PCB serial number.

    meter_type controls which table is searched:
      - a string containing 'better' -> BETTER1P_CALIB only
      - anything else (e.g. 'garud_1ph') -> GARUD1P_CALIB only
      - None (default) -> both tables are searched and results merged,
        since the serial number alone doesn't say which meter type it was

    Returns a list of dicts (db_column_name -> value), one per matching row,
    newest first if the table has a date_time column, with an extra
    "_table" key noting which table each row came from. Returns [] if
    nothing matches, the DB is unreachable, or the query fails -- callers
    don't need to distinguish "no match" from "lookup failed" unless they
    check logs.

    calibration test scripts run one worker thread per COM port and every
    one of them calls this function against the single shared Athena
    connection, so the actual query is serialized on _conn_lock -- psycopg2
    connections aren't safe to use concurrently from multiple threads. If
    the connection turns out to be dead (server dropped an idle connection,
    a network blip, etc.) it's dropped and one reconnect+retry is attempted
    before giving up, so a single transient DB hiccup isn't reported as a
    genuine calibration "fail" for the meter.
    """
    global _athena_con

    pcb_column = "meter_pcb_serial_no"

    tables = ["pct_logs"]

    for attempt in range(2):
        conn = _get_connection('athena')
        if conn is None:
            logging.error(
                "Database connection not available for PCB serial lookup (attempt %d/2)",
                attempt + 1,
            )
            continue

        results = []
        try:
            with _conn_lock:
                with conn.cursor() as cursor:
                    for table_name in tables:
                        db_columns = _table_columns(cursor, table_name, TABLE_SCHEMA_ATHENA)
                        # print(db_columns)
                        if pcb_column not in db_columns:
                            # This table doesn't have the column at all -- skip it
                            # rather than erroring, so a meter_type=None search
                            # still works even if one table's schema is older.
                            logging.warning(
                                '"%s"."%s" has no "%s" column -- skipping in PCB serial lookup',
                                TABLE_SCHEMA_ATHENA, table_name, pcb_column,
                            )
                            continue

                        # Sort by the actual test time, not by ingested_at:
                        # ingested_at only reflects when the S3->DB loader
                        # happened to process a row, which is not guaranteed
                        # to match the real order the PCT attempts ran in
                        # (e.g. a batch load can insert an earlier failed
                        # attempt a moment after a later passed retest). That
                        # mismatch was returning stale FAIL rows for meters
                        # that had already passed on retest. test_time is the
                        # PCT station's own timestamp for when that attempt
                        # actually ran, so it reflects the true latest attempt.
                        order_column = "test_time" if "test_time" in db_columns else "ingested_at"
                        query = sql.SQL(
                            "SELECT * FROM {}.{} WHERE {} = {} ORDER BY {} DESC LIMIT 1"
                        ).format(
                            sql.Identifier(TABLE_SCHEMA_ATHENA),
                            sql.Identifier(table_name),
                            sql.Identifier(pcb_column),
                            sql.Placeholder(),
                            sql.Identifier(order_column),
                        )
                        logging.info("Executing PCB serial lookup query: %s", query.as_string(cursor))
                        cursor.execute(query, (pcb_serial_no,))
                        columns = [desc[0] for desc in cursor.description]
                        for row in cursor.fetchall():
                            row_dict = dict(zip(columns, row))
                            row_dict["_table"] = table_name
                            results.append(row_dict)
            logging.info(
                "PCB serial lookup for %s returned %d row(s) across %s: %s",
                pcb_serial_no, len(results), tables, results,
            )
            if results:
                return results[0]['overall_result'].lower() == 'pass'
            return False
        except psycopg2.Error as exc:
            try:
                conn.rollback()
            except Exception:
                pass
            logging.error(
                "PCB serial lookup failed for %s (attempt %d/2): %s",
                pcb_serial_no, attempt + 1, exc,
            )
            with _conn_lock:
                # Drop the shared connection so the next attempt (this
                # retry, or the next call) reconnects instead of reusing
                # the same broken connection object.
                if _athena_con is conn:
                    _athena_con = None

    return False


# print(fetch_by_pcb_serial('P26090601000000100701632418','garud_1p'))