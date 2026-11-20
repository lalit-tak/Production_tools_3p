# 3-Phase LTCT / WC PCT Tool (v3.12)

Production/PCB Calibration Test (PCT) tool for 3-phase meters (**LTCT** and **WC** variants). It talks to several meters in parallel over serial (IrDA/COM) ports, runs a fixed sequence of test cases on each, logs results to Excel, and optionally uploads them to a PostgreSQL database and AWS S3.

## Files

| File | Purpose |
|---|---|
| `pct_multiport.py` | Main entry point. Prompts for serial numbers, runs one thread per COM port, writes Excel log, uploads results, shows summary popup. |
| `Test_cases_verificationClass.py` | `TestCasePCTMCT` class: individual meter commands/test cases (current, voltage, relay, serial numbers, versions, GPRS, DIDO, etc.). |
| `config.py` | `Config` class: loads `config.json`, decrypts and validates `config_file.enc` (PBKDF2 + Fernet, SHA-256 checksum). |
| `db_connect.py` | PostgreSQL upload (`upload_dataframe`), column mappings for LTCT/WC, local pending-queue fallback. |
| `config.json` | Local, plain-text port configuration (see below). |
| `config_file.enc` | Encrypted test-parameter configuration (see below). |
| `requirements.txt` | Python dependencies. |

## Setup

1. Windows + Python 3.9+ (uses `pywin32`, `tkinter`).
2. `pip install -r requirements.txt`
3. Install the internal `gp_node` package (not on PyPI).
4. Fill in the placeholders before running:
   - `config.py`: `PASSWORD` (config decryption password), `CHECKSUMPASS`.
   - `db_connect.py`: `DB_CONFIG`, `TABLE_SCHEMA`, `PENDING_FILE`.
   - `pct_multiport.py`: `ACCESS_KEY`, `SECRET_KEY`, `bucket_name`, `folder_name` (AWS S3).
   
   > Never commit real credentials. Prefer environment variables or a secrets store.
5. Run: `python pct_multiport.py`

## Usage

1. Start the tool. It loads `config.json` and validates `config_file.enc`.
2. For each configured COM port (meter position) enter:
   - **Meter PCB serial number** – characters 9–16 must equal `Main_PCB_SFG_Prefix`; last 8 characters must be digits (they become the meter serial number).
   - **NIC PCB serial number** – starts with `r144`, or characters 9–16 equal `NIC_PCB_SFG_PREFIX`.
3. Press Enter to start. All ports are tested concurrently.
4. After the run, re-enter the Meter PCB serial number printed on each board; a mismatch with the one written inside the meter marks that meter as **fail**.
5. A colored console summary and a popup show Passed / Failures / Unreachable ports. The tool then loops for the next batch.

## Test sequence

Live-version/port check → Factory Reset → Verify Current (all CTs, reverse-CT tamper check) → Verify Voltage → *Relay Off (WC only)* → Set Time → Set Meter PCB No → Set NIC PCB No → Calibration Unlock → Set Meter Serial No → Set Manufacturing Year (optional) → Get Live Version → Get Internal Version (optional) → *Verify DIDO (LTCT only, optional)* → Verify Bootloader Version → *Verify Current after Relay Off + Relay On (WC only)* → Set Sim Toggle (optional) → Set/Get GPRS Protocol → PCB serial cross-check.

Each step retries up to 3 times.

## Configuration files

### `config.json` (plain JSON, local per-bench)

| Key | Type | Description |
|---|---|---|
| `com_port` | list[int] | COM port numbers to test, e.g. `[3]` -> `COM3`. One meter position per entry. Required (tool exits if empty). |
| `upload_bench` | string | Bench identifier, prefixed to uploaded S3 file names. Defaults to `"1"`. |

Example:

```json
{
    "com_port": [3, 4, 5, 6],
    "upload_bench": "1"
}
```

### `config_file.enc` (encrypted, shared test parameters)

Binary file: first 16 bytes = salt, remainder = Fernet token (key derived with PBKDF2-HMAC-SHA256, 390000 iterations). Decrypted content is a JSON object with `encrypted_data` and `checksum`; `encrypted_data` is itself Fernet-encrypted with `CHECKSUMPASS` and its SHA-256 checksum must match, otherwise the file is rejected as corrupted. `TOOL_TYPE` must contain `pct`.

Keys inside the final decrypted JSON:

| Key | Default | Description |
|---|---|---|
| `TOOL_TYPE` | `img_pct` | Tool name; must contain `pct`. Used in log file / sheet names. |
| `METER_TYPE` | `3PWC` | Must contain `ltct` or `wc`. Selects test sequence, DB table and column mapping. |
| `RETRIES` | `3` | Per-command retry count in the test-case class. |
| `FACTORY_RESET` | `True` | Set to `False` to skip factory reset. |
| `FACTORY_RESET_SLEEP_TIME` (legacy `Fact_Reset_sleepTime`) | `5` | Seconds to wait after factory reset. |
| `I_PHASE_MIN` / `I_PHASE_MAX` | `0.0` / `4.0` | Allowed current range (A) for R, Y, B, N phases. |
| `Voltage_Min` / `Voltage_Max` | `0.0` / `0.0` | Allowed voltage range (V) for R, Y, B phases. |
| `MANUFACTURING_YEAR_SET` | `False` | `True` to write the manufacturing year. |
| `MANUFACTURING_YEAR` | `""` | Year to write when enabled. |
| `LIVE_VERSION` | `""` | Expected firmware live version (exact match). |
| `INTERNAL_VERSION` | `"0"` | Expected internal version; `"0"` skips the check. |
| `BOOTLOADER_VERSION` | `""` | Expected bootloader version (float compare). |
| `VERIFY_DIDO_STATUS` | `False` | LTCT only: `True` to verify DIDO status equals `1111`. |
| `SET_SIM_TOGGLE` | `False` | `True` to run the SIM toggle test. |
| `Main_PCB_SFG_Prefix` | `""` | Expected chars 9–16 of the Meter PCB serial number. |
| `NIC_PCB_SFG_PREFIX` | `""` | Expected chars 9–16 of the NIC PCB serial number. |
| `IS_DATA_CONN` | `1` | `1` = upload to PostgreSQL, then S3 on success; `0` = S3 upload only. |
| `Thread_start_delay` | `0.5` | Seconds between starting per-port threads. |
| `Thread_timeout` | `40` | Seconds to wait for each port thread before moving on. |

Note: `FACTORY_RESET`, `MANUFACTURING_YEAR_SET`, `VERIFY_DIDO_STATUS` and `SET_SIM_TOGGLE` are compared as strings in code (`str(True)` / `str(False)`).

## Outputs

- **Excel log**: `<METER_TYPE>_<TOOL_TYPE>_LOG.xlsx` in the working directory (created automatically with headers).
- **Application log**: `Logs/PCT.log`, rotated daily, 7 days kept.
- **Database**: `LTCT3P_PCT` (LTCT) or `WC3P_PCT` (WC) table in the configured schema.
- **S3**: `<folder_name>/<meter folder>/PCT/<date>/<bench>_<time>_<file>.xlsx`; the local file is deleted after a successful upload.
- **Pending queue**: failed DB payloads can be queued to `PENDING_FILE` as JSON lines.
