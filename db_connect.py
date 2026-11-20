import datetime
import json
import logging
import os

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json



DB_CONFIG = {
    "host": PUT_YOUR_HOST_HERE,
    "port": PUT_YOUR_PORT_HERE,
    "database": PUT_YOUR_DATABASE_HERE,
    "user": PUT_YOUR_USER_HERE,
    "password": PUT_YOUR_PASSWORD_HERE,
}
TABLE_SCHEMA = PUT_YOUR_TABLE_SCHEMA_HERE

PENDING_FILE = PUT_YOUR_PENDING_FILE_PATH_HERE

_conn = None

# COLUMN_MAPPING_LTCT = {
#     "MAC_ADDR": "mac_addr",
#     "Index": "index",
#     "Date_time": "date_time",
#     "Duplicate_Serial_No": "duplicate_serial_no",
#     "Live_Version": "live_version",
#     "Meter_PCB_Serial_No": "meter_pcb_serial_no",
#     "Nic_PCB_No": "nic_pcb_no",
#     "Meter_IP_Address": "meter_ip_address",
#     "CalibStatus": "calibstatus",
#     "FrequencyCoeff": "frequencycoeff",
#     "VCoeff[R]": "vcoeff_r",
#     "VCoeff[Y]": "vcoeff_y",
#     "VCoeff[B]": "vcoeff_b",
#     "ICoeff[R]": "icoeff_r",
#     "ICoeff[Y]": "icoeff_y",
#     "ICoeff[B]": "icoeff_b",
#     "ICoeff[N]": "icoeff_n",
#     "ActPowerCoeff[R]": "actpowercoeff_r",
#     "ActPowerCoeff[Y]": "actpowercoeff_y",
#     "ActPowerCoeff[B]": "actpowercoeff_b",
#     "PhAngle[R]": "phangle_r",
#     "PhAngle[Y]": "phangle_y",
#     "PhAngle[B]": "phangle_b",
#     "FinalPhAngle[R]": "finalphangle_r",
#     "FinalPhAngle[Y]": "finalphangle_y",
#     "FinalPhAngle[B]": "finalphangle_b",
#     "VFCoeff[R]": "vfcoeff_r",
#     "VFCoeff[Y]": "vfcoeff_y",
#     "VFCoeff[B]": "vfcoeff_b",
#     "IFCoeff[R]": "ifcoeff_r",
#     "IFCoeff[Y]": "ifcoeff_y",
#     "IFCoeff[B]": "ifcoeff_b",
#     "IFCoeff[N]": "ifcoeff_n",
#     "PhAngleF[R]": "phanglef_r",
#     "PhAngleF[Y]": "phanglef_y",
#     "PhAngleF[B]": "phanglef_b",
#     "Internal_Version": "internal_version",
#     "Set_Time_Value": "set_time_value",
#     "Led_Apparent_Value": "led_apparent_value",
#     "Overall_Result": "overall_result",
#     "Meter_Serial_Num": "meter_serial_num",
#     "live_version": "live_version_1",
#     "Get_Meter_PCB_No": "get_meter_pcb_no",
#     "Get_Nic_PCB_No": "get_nic_pcb_no",
#     "Get_Meter_Address": "get_meter_address",
#     "Get_3p_calib_cofficient": "get_3p_calib_cofficient",
#     "Get_Internal_Version": "get_internal_version",
#     "Set_Time": "set_time",
#     "Verify_time": "verify_time",
#     "Calibration_Unlock": "calibration_unlock",
#     "Clear_Energy": "clear_energy",
#     "Verify_DLMS_Activation": "verify_dlms_activation",
#     "Factory_Reset": "factory_reset",
#     "Check_Num_Events": "check_num_events",
#     "Check_Apparent_Led": "check_apparent_led"
# }

COLUMN_MAPPING_LTCT = {
    "MAC_ADDR": "mac_addr",
    "Index": "index",
    "Date_time": "date_time",
    "CurrentR": "currentr",
    "CurrentY": "currenty",
    "CurrentB": "currentb",
    "CurrentN": "currentn",
    "live_tamper": "live_tamper",
    "VoltageR": "voltager",
    "VoltageY": "voltagey",
    "VoltageB": "voltageb",
    "Set_Time_Value": "set_time_value",
    "Meter_PCB_Serial_No": "meter_pcb_serial_no",
    "Nic_PCB_No": "nic_pcb_no",
    "Meter_SERIAL_NUM": "meter_serial_num_orig",
    "Manufacturing_Year": "manufacturing_year",
    "Live_Version": "live_version",
    "Internal_Version": "internal_version",
    "DIDO_Value": "dido_value",
    "Bootloader_Version": "bootloader_version",
    "GPRS_Protocol": "gprs_protocol",
    "Overall_Result": "overall_result",
    "Factory_Reset": "factory_reset",
    "Verify_Current_in_all_CT": "verify_current_in_all_ct",
    "Verify_Voltage": "verify_voltage",
    "Set_Time": "set_time",
    "Set_Meter_PCB_No": "set_meter_pcb_no",
    "Set_Nic_PCB_No": "set_nic_pcb_no",
    "Calibration_Unlock": "calibration_unlock",
    "Meter_Serial_Num": "meter_serial_num",
    "Set_Manufacturing_Year": "set_manufacturing_year",
    "live_version": "live_version_1",
    "Get_Internal_Version": "get_internal_version",
    "Verify_DIDO_Status": "verify_dido_status",
    "Verify_Bootloader_Version": "verify_bootloader_version",
    "Set_Sim_Toggle": "set_sim_toggle",
    "Set_GPRS_Protocol": "set_gprs_protocol",
    "Get_GPRS_Protocol": "get_gprs_protocol"
}

COLUMN_MAPPING_WC = {
    "MAC_ADDR": "mac_addr",
    "Index": "index",
    "Date_time": "date_time",
    "CurrentR": "currentr",
    "CurrentY": "currenty",
    "CurrentB": "currentb",
    "CurrentN": "currentn",
    "live_tamper": "live_tamper",
    "VoltageR": "voltager",
    "VoltageY": "voltagey",
    "VoltageB": "voltageb",
    "Set_Time_Value": "set_time_value",
    "Meter_PCB_Serial_No": "meter_pcb_serial_no",
    "Nic_PCB_No": "nic_pcb_no",
    "Meter_SERIAL_NUM": "meter_serial_num_orig",
    "Manufacturing_Year": "manufacturing_year",
    "Live_Version": "live_version",
    "Internal_Version": "internal_version",
    "Bootloader_Version": "bootloader_version",
    "CurrentR_After_Relay_Off": "currentr_after_relay_off",
    "CurrentY_After_Relay_Off": "currenty_after_relay_off",
    "CurrentB_After_Relay_Off": "currentb_after_relay_off",
    "CurrentN_After_Relay_Off": "currentn_after_relay_off",
    "Live_Temper_After_Relay_Off": "live_temper_after_relay_off",
    "GPRS_Protocol": "gprs_protocol",
    "Overall_Result": "overall_result",
    "Factory_Reset": "factory_reset",
    "Verify_Current_in_all_CT": "verify_current_in_all_ct",
    "Verify_Voltage": "verify_voltage",
    "Relay Off": "relay_off",
    "Set_Time": "set_time",
    "Set_Meter_PCB_No": "set_meter_pcb_no",
    "Set_Nic_PCB_No": "set_nic_pcb_no",
    "Calibration_Unlock": "calibration_unlock",
    "Meter_Serial_Num": "meter_serial_num",
    "Set_Manufacturing_Year": "set_manufacturing_year",
    "live_version": "live_version_1",
    "Get_Internal_Version": "get_internal_version",
    "Verify_Bootloader_Version": "verify_bootloader_version",
    "After Relay Off Verify Current": "after_relay_off_verify_current",
    "Relay On": "relay_on",
    "Set_Sim_Toggle": "set_sim_toggle",
    "Set_GPRS_Protocol": "set_gprs_protocol",
    "Get_GPRS_Protocol": "get_gprs_protocol"
}


def start_connection():
    global _conn

    if _conn and not _conn.closed:
        return _conn

    try:
        _conn = psycopg2.connect(connect_timeout=5, **DB_CONFIG)
        _conn.autocommit = False
        logging.info("Database connection started")
        return _conn
    except Exception as exc:
        _conn = None
        logging.error("Database connection failed: %s", exc)
        return None

def close_connection():
    global _conn

    if _conn and not _conn.closed:
        try:
            _conn.close()
            logging.info("Database connection closed")
        except Exception as exc:
            logging.error("Error while closing database connection: %s", exc)
    _conn = None

def _get_connection():
    if _conn is None or _conn.closed:
        return start_connection()
    return _conn

def _build_payload(log):
    return {
        "mac_address": log[0] if len(log) > 0 else None,
        "meter_info": list(log[1]) if len(log) > 1 else [],
        "test_result": list(log[2]) if len(log) > 2 else [],
        "book_name": log[3] if len(log) > 3 else None,
        "file_name": log[4] if len(log) > 4 else None,
        "created_at": datetime.datetime.now().isoformat(),
    }

def _table_columns(cursor, table_name):
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """,
        (TABLE_SCHEMA, table_name),
    )
    return [row[0] for row in cursor.fetchall()]

def _insert_payload(cursor, payload):
    columns = _table_columns(cursor)
    payload_column = next(
        (
            column
            for column in ("payload", "data", "json_data", "result_json", "MCT_data")
            if column in columns
        ),
        None,
    )

    if payload_column:
        insert_columns = [payload_column]
        values = [Json(payload)]
    else:
        insert_columns = [column for column in payload.keys() if column in columns]
        values = [Json(payload[column]) if isinstance(payload[column], list) else payload[column] for column in insert_columns]

    if not insert_columns:
        raise RuntimeError(
            'No matching columns found in "{}"."{}" for MCT upload'.format(
                TABLE_SCHEMA, TABLE_NAME
            )
        )

    query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
        sql.Identifier(TABLE_SCHEMA),
        sql.Identifier(TABLE_NAME),
        sql.SQL(", ").join(map(sql.Identifier, insert_columns)),
        sql.SQL(", ").join(sql.Placeholder() * len(insert_columns)),
    )
    cursor.execute(query, values)

def upload_log(log):
    payload = _build_payload(log)
    conn = _get_connection()

    if conn is None:
        _queue_payload(payload)
        return False

    try:
        with conn.cursor() as cursor:
            _insert_payload(cursor, payload)
        conn.commit()
        logging.info("MCT row uploaded to database")
        return True
    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        logging.error("MCT database upload failed, queued locally: %s", exc)
        _queue_payload(payload)
        return False

def upload_dataframe(df_frame, meter_type):
    if 'ltct' in meter_type:
        mapping = COLUMN_MAPPING_LTCT
        TABLE_NAME = "LTCT3P_PCT"
    else:
        mapping = COLUMN_MAPPING_WC
        TABLE_NAME = "WC3P_PCT"
    missing_cols = [col for col in mapping if col not in df_frame.columns]
    if missing_cols:
        error_msg = f"DataFrame is missing expected columns: {missing_cols}"
        logging.error(error_msg)
        return False, error_msg

    df_renamed = df_frame.rename(columns=mapping)
    df_renamed["date"] = datetime.date.today()

    conn = _get_connection()
    if conn is None:
        error_msg = "Database connection not available"
        logging.error(error_msg)
        return False, error_msg

    try:
        with conn.cursor() as cursor:
            db_columns = _table_columns(cursor, TABLE_NAME)
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
                values = [
                    Json(row[col]) if isinstance(row[col], (list, dict)) else row.get(col, None) if col != db_columns_lower.get("date") else row["date"]
                    for col in insert_columns
                ]
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

def _queue_dataframe(df_frame, source_label):
    """Fallback: queue dataframe rows locally as JSON lines if DB upload fails."""
    try:
        with open(PENDING_FILE, "a", encoding="utf-8") as pending_file:
            for record in df_frame.to_dict(orient="records"):
                record["_source"] = source_label
                pending_file.write(json.dumps(record, default=str) + "\n")
    except Exception as exc:
        logging.error("Failed to queue dataframe locally: %s", exc)

def _queue_payload(payload):
    with open(PENDING_FILE, "a", encoding="utf-8") as pending_file:
        pending_file.write(json.dumps(payload, default=str) + "\n")

def upload_pending():
    if not os.path.exists(PENDING_FILE):
        return 0

    conn = _get_connection()
    if conn is None:
        return 0

    uploaded_count = 0
    remaining = []

    with open(PENDING_FILE, "r", encoding="utf-8") as pending_file:
        for line in pending_file:
            line = line.strip()
            if not line:
                continue

            try:
                payload = json.loads(line)
                with conn.cursor() as cursor:
                    _insert_payload(cursor, payload)
                conn.commit()
                uploaded_count += 1
            except Exception as exc:
                try:
                    conn.rollback()
                except Exception:
                    pass
                logging.error("Pending MCT database upload still failed: %s", exc)
                remaining.append(line)

    if remaining:
        with open(PENDING_FILE, "w", encoding="utf-8") as pending_file:
            pending_file.write("\n".join(remaining) + "\n")
    else:
        os.remove(PENDING_FILE)

    if uploaded_count:
        logging.info("Uploaded %s pending MCT database rows", uploaded_count)
    return uploaded_count

def execute_query():
    conn = _get_connection()
    if conn is None:
        print("Database connection is not available")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM "Prod"."MCT" LIMIT 10;')
            columns = [desc[0] for desc in cursor.description]
            print(f"Columns: {columns}\n")
            rows = cursor.fetchall()
            print(f"Total rows fetched: {len(rows)}\n")

            for i, row in enumerate(rows, 1):
                print(f"Row {i}: {row}")

    except psycopg2.Error as exc:
        print("Database error:", str(exc))
    except Exception as exc:
        print("Error:", str(exc))
