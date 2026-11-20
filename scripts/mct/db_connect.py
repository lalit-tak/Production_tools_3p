import datetime
import json
import logging
import os
import threading

import pandas as pd
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
# ============================================
# GARUD — rf_mct / img_mct
# ============================================
COLUMN_MAPPING_GARUD_MCT = {
    "MAC_ADDR": "mac_addr",
    "Index": "index",
    "Date_time": "date_time",
    "Duplicate_Serial_No": "duplicate_serial_no",
    "Live_Version": "live_version",
    "Meter_PCB_Serial_No": "meter_pcb_serial_no",
    "Nic_PCB_No": "nic_pcb_no",
    "Meter_IP_Address": "meter_ip_address",
    "CalibSign": "calib_sign",
    "FrequencyCoeff": "frequency_coeff",
    "VCoeff": "v_coeff",
    "ICoeff[0]": "i_coeff_0",
    "ICoeff[1]": "i_coeff_1",
    "ActPowerCoeff[0]": "act_power_coeff_0",
    "ActPowerCoeff[1]": "act_power_coeff_1",
    "PhAngle[0]": "ph_angle_0",
    "PhAngle[1]": "ph_angle_1",
    "Internal_Version": "internal_version",
    "Set_Meter_time": "set_meter_time",
    "Payment_Mode_Value":"payment_mode_value",
    "Hardware_version": "hardware_version",
    "Start_I_StartingEnergyIn10Min": "start_i_startingenergyin10min",
    "Final_I_StartingEnergyIn10Min": "final_i_startingenergyin10min",
    "I_StartingEnergyIn10Min": "i_starting_energy_in_10min",
    "Stand_I_StartingEnergyIn10Min": "stand_i_startingenergyin10min",
    "Start_No_Load_EnergyIn10Min": "start_no_load_energyin10min",
    "Final_No_Load_EnergyIn10Min": "final_no_load_energyin10min",
    "No_Load_EnergyIn10Min": "no_load_energy_in_10min",
    "Stand_No_Load_EnergyIn10Min": "stand_no_load_energyin10min", 
    "Overall_Result": "overall_result",
    "Meter_Serial_Num": "meter_serial_num",
    "live_version": "live_version_result",
    "Get_Meter_PCB_No": "get_meter_pcb_no",
    "Get_Nic_PCB_No": "get_nic_pcb_no",
    "Get_Meter_Address": "get_meter_address",
    "Get_1p_calib_cofficient": "get_1p_calib_coefficient",
    "Get_Internal_Version": "get_internal_version",
    "Set_Time": "set_time",
    "verify_time": "verify_time",
    "Calibration_Unlock": "calibration_unlock",
    "Clear_Energy": "clear_energy",
    "Payment_Mode": "payment_mode",
    "Get_HW_Version": "get_hw_version",
    "Verify_DLMS_Activation": "verify_dlms_activation",
    "Verify_Starting_Current_Test": "verify_starting_current_test",
    "Factory_Reset": "factory_reset",
    "Check_Num_Events": "check_num_events",
    "Verify_No_Load_Test": "verify_no_load_test",
    "Calib_Unlock_No_Load": "calib_unlock_no_load",
    "Clear_Energy_No_Load": "clear_energy_no_load",
}

# ============================================
# BETTER — rf_mct / img_mct  (no Get_HW_Version)
# ============================================
COLUMN_MAPPING_BETTER_MCT = {
    "MAC_ADDR": "mac_addr",
    "Index": "index",
    "Date_time": "date_time",
    "Duplicate_Serial_No": "duplicate_serial_no",
    "Live_Version": "live_version",
    "Meter_PCB_Serial_No": "meter_pcb_serial_no",
    "Nic_PCB_No": "nic_pcb_no",
    "Meter_IP_Address": "meter_ip_address",
    "CalibSign": "calib_sign",
    "FrequencyCoeff": "frequency_coeff",
    "VCoeff": "v_coeff",
    "ICoeff[0]": "i_coeff_0",
    "ICoeff[1]": "i_coeff_1",
    "ActPowerCoeff[0]": "act_power_coeff_0",
    "ActPowerCoeff[1]": "act_power_coeff_1",
    "PhAngle[0]": "ph_angle_0",
    "PhAngle[1]": "ph_angle_1",
    "Internal_Version": "internal_version",
    "Set_Meter_time": "set_meter_time",
    "Payment_Mode_Value":"payment_mode_value",
    "Start_I_StartingEnergyIn10Min": "start_i_startingenergyin10min",
    "Final_I_StartingEnergyIn10Min": "final_i_startingenergyin10min",
    "I_StartingEnergyIn10Min": "i_starting_energy_in_10min",
    "Stand_I_StartingEnergyIn10Min": "stand_i_startingenergyin10min",
    "Start_No_Load_EnergyIn10Min": "start_no_load_energyin10min",
    "Final_No_Load_EnergyIn10Min": "final_no_load_energyin10min",
    "No_Load_EnergyIn10Min": "no_load_energy_in_10min",
    "Stand_No_Load_EnergyIn10Min": "stand_no_load_energyin10min", 
    "Overall_Result": "overall_result",
    "Meter_Serial_Num": "meter_serial_num",
    "live_version": "live_version_result",
    "Get_Meter_PCB_No": "get_meter_pcb_no",
    "Get_Nic_PCB_No": "get_nic_pcb_no",
    "Get_Meter_Address": "get_meter_address",
    "Get_1p_calib_cofficient": "get_1p_calib_coefficient",
    "Get_Internal_Version": "get_internal_version",
    "Set_Time": "set_time",
    "verify_time": "verify_time",
    "Calibration_Unlock": "calibration_unlock",
    "Clear_Energy": "clear_energy",
    "Payment_Mode": "payment_mode",
    "Verify_DLMS_Activation": "verify_dlms_activation",
    "Verify_Starting_Current_Test": "verify_starting_current_test",
    "Factory_Reset": "factory_reset",
    "Check_Num_Events": "check_num_events",
    "Verify_No_Load_Test": "verify_no_load_test",
    "Calib_Unlock_No_Load": "calib_unlock_no_load",
    "Clear_Energy_No_Load": "clear_energy_no_load",
}

# ============================================
# GARUD — 4g_mct
# ============================================
COLUMN_MAPPING_GARUD_4G_MCT = {
    "MAC_ADDR": "mac_addr",
    "Index": "index",
    "Date_time": "date_time",
    "Duplicate_Serial_No": "duplicate_serial_no",
    "Live_Version": "live_version",
    "Meter_PCB_Serial_No": "meter_pcb_serial_no",
    "Nic_PCB_No": "nic_pcb_no",
    "Meter_IP_Address": "meter_ip_address",
    "CalibSign": "calib_sign",
    "FrequencyCoeff": "frequency_coeff",
    "VCoeff": "v_coeff",
    "ICoeff[0]": "i_coeff_0",
    "ICoeff[1]": "i_coeff_1",
    "ActPowerCoeff[0]": "act_power_coeff_0",
    "ActPowerCoeff[1]": "act_power_coeff_1",
    "PhAngle[0]": "ph_angle_0",
    "PhAngle[1]": "ph_angle_1",
    "Internal_Version": "internal_version",
    "Set_Meter_time": "set_meter_time",
    "Payment_Mode_Value":"payment_mode_value",
    "Hardware_version": "hardware_version",
    "Active_Sim": "active_sim",
    "SIM_NUM": "sim_num",
    "APN": "apn",
    "IMEI": "imei",
    "Signal_Strength": "signal_strength",
    "Overall_Result": "overall_result",
    "Meter_Serial_Num": "meter_serial_num",
    "live_version": "live_version_result",
    "Get_Meter_PCB_No": "get_meter_pcb_no",
    "Get_Nic_PCB_No": "get_nic_pcb_no",
    "Get_Meter_Address": "get_meter_address",
    "Get_1p_calib_cofficient": "get_1p_calib_coefficient",
    "Get_Internal_Version": "get_internal_version",
    "Set_Time": "set_time",
    "verify_time": "verify_time",
    "Calibration_Unlock": "calibration_unlock",
    "Clear_Energy": "clear_energy",
    "Payment_Mode": "payment_mode",
    "Get_HW_Version": "get_hw_version",
    "Verify_DLMS_Activation": "verify_dlms_activation",
    "check_GPRS_connection": "check_gprs_connection",
    "Factory_Reset": "factory_reset",
    "Check_Num_Events": "check_num_events",
}

# ============================================
# BETTER — 4g_mct  (no Get_HW_Version)
# ============================================
COLUMN_MAPPING_BETTER_4G_MCT = {
    "MAC_ADDR": "mac_addr",
    "Index": "index",
    "Date_time": "date_time",
    "Duplicate_Serial_No": "duplicate_serial_no",
    "Live_Version": "live_version",
    "Meter_PCB_Serial_No": "meter_pcb_serial_no",
    "Nic_PCB_No": "nic_pcb_no",
    "Meter_IP_Address": "meter_ip_address",
    "CalibSign": "calib_sign",
    "FrequencyCoeff": "frequency_coeff",
    "VCoeff": "v_coeff",
    "ICoeff[0]": "i_coeff_0",
    "ICoeff[1]": "i_coeff_1",
    "ActPowerCoeff[0]": "act_power_coeff_0",
    "ActPowerCoeff[1]": "act_power_coeff_1",
    "PhAngle[0]": "ph_angle_0",
    "PhAngle[1]": "ph_angle_1",
    "Internal_Version": "internal_version",
    "Set_Meter_time": "set_meter_time",
    "Payment_Mode_Value":"payment_mode_value",
    "Active_Sim": "active_sim",
    "SIM_NUM": "sim_num",
    "APN": "apn",
    "IMEI": "imei",
    "Signal_Strength": "signal_strength",
    "Overall_Result": "overall_result",
    "Meter_Serial_Num": "meter_serial_num",
    "live_version": "live_version_result",
    "Get_Meter_PCB_No": "get_meter_pcb_no",
    "Get_Nic_PCB_No": "get_nic_pcb_no",
    "Get_Meter_Address": "get_meter_address",
    "Get_1p_calib_cofficient": "get_1p_calib_coefficient",
    "Get_Internal_Version": "get_internal_version",
    "Set_Time": "set_time",
    "verify_time": "verify_time",
    "Calibration_Unlock": "calibration_unlock",
    "Clear_Energy": "clear_energy",
    "Payment_Mode": "payment_mode",
    "Verify_DLMS_Activation": "verify_dlms_activation",
    "check_GPRS_connection": "check_gprs_connection",
    "Factory_Reset": "factory_reset",
    "Check_Num_Events": "check_num_events",
}

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

def _clean_value_for_db(value):
    """Convert pandas/numpy missing-value markers (NaN, NaT, None) into a
    real Python None, so psycopg2 sends an actual SQL NULL instead of a
    'double precision' NaN literal - which Postgres rejects for any
    non-numeric column. This is exactly what was causing:

        column "date_time" is of type timestamp without time zone but
        expression is of type double precision

    A missing/None value written by the test scripts (see
    fill_missing_fields() / NOT_TESTED_METER_VALUE in mct_multiport.py)
    round-trips through Excel via pd.read_excel() as NaN, regardless of
    what the column's real type is meant to be - a timestamp column, a
    text column, a boolean column, all become NaN the same way once the
    cell was ever empty. So this cleaning is applied to every column
    here, not just Date_time; any fully- or partially-untested port's
    other missing fields would hit the identical error against their own
    column types otherwise.

    isinstance check for list/dict comes first because pd.isna() raises/
    behaves oddly on those rather than returning a clean boolean, and
    they're already handled separately by the Json() wrapper at the call
    site."""
    if isinstance(value, (list, dict)):
        return value
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value

def upload_dataframe(df_frame, meter_type, tool_type):
    global TABLE_SCHEMA
    if 'better' in meter_type:
        if '4g' in tool_type:
            TABLE_NAME = "BETTER_4G_MCT"
            mapping = COLUMN_MAPPING_BETTER_4G_MCT
        else:
            TABLE_NAME = "BETTER_MCT"
            mapping = COLUMN_MAPPING_BETTER_MCT
    else:
        # TABLE_NAME = "GARUD_MCT"
        if '4g' in tool_type:
            TABLE_NAME = "GARUD_4G_MCT"
            mapping = COLUMN_MAPPING_GARUD_4G_MCT
        else:
            TABLE_NAME = "GARUD_MCT"
            mapping = COLUMN_MAPPING_GARUD_MCT
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
            # logging.debug(f"table columns: {db_columns}")
            # logging.debug(f"dataframe: {list(df_frame.columns)}")
            db_columns_lower = {c.lower(): c for c in db_columns}  # map lower -> real name

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
                values = []
                for col in insert_columns:
                    raw_value = row["date"] if col == db_columns_lower.get("date") else row.get(col, None)
                    if isinstance(raw_value, (list, dict)):
                        values.append(Json(raw_value))
                    else:
                        values.append(_clean_value_for_db(raw_value))
                logging.debug(f"insert value in mct table: {values}")
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

def fetch_by_pcb_serial(pcb_serial_no, tool_type = 'img'):
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

    mct_multiport.py runs one worker thread per COM port and every one of
    them calls this function against the single shared Athena connection,
    so the actual query is serialized on _conn_lock -- psycopg2 connections
    aren't safe to use concurrently from multiple threads. If the
    connection turns out to be dead (server dropped an idle connection,
    a network blip, etc.) it's dropped and one reconnect+retry is attempted
    before giving up, so a single transient DB hiccup isn't reported as a
    genuine RTT/PCT "fail" for the meter.
    """
    global _athena_con

    if tool_type.lower() == "img":
        pcb_column = "pcb_serial_no"
    else:
        pcb_column = "pcb_serial_num"

    tables = ["rtt_logs"]

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

                        # Sort by the actual test time, not ingested_at:
                        # ingested_at only reflects when the S3->DB loader
                        # happened to process a row, which can land an
                        # earlier failed attempt's row after a later passed
                        # retest's row, returning a stale FAIL. test_time is
                        # the station's own timestamp for when that attempt
                        # actually ran.
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


# print(fetch_by_pcb_serial('P26063001000008000600135016', 'img'))