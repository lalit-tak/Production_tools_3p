# Production Tool Bench – 3-Phase Single UI (v3.0)

A single-window PyQt5 application for the 3-phase (3P) production bench. One screen runs the complete bench flow – **Check Ports, Calibration (Phase & Neutral), RTT, DLMS and MCT** – across all configured COM ports and shows live pass/fail results per meter in two side-by-side tables.

## Features

- **Single UI** – header shows logo, bench number, Project, Live/Internal firmware versions and Meter Type; toolbar holds the test buttons and tool version.
- **Multi-port testing** – COM ports from `config.json` are split across two tables. Columns: COM port, PCBA serial, Phase, Neutral, RTT, DLMS, MCT, Status.
- **Toolbar workflow** – New Batch, Check Ports, Calibration, RTT Test, DLMS Test, MCT Test. Icons: ○ not run, ⧖ running, ✓ done. The running button turns purple and all others are locked; New Batch is blocked while a test runs.
- **Colour-coded results** – port name gold while running, green on pass, red on fail.
- **Statistics bar** – time, pass and fail counts per test, Elapsed Time, Total Executed Cycles (not reset by New Batch).
- **Serial number check** – Check Ports verifies the PCBA serial against `MAIN_PCB_SFG_PREFIX`.
- **Excel report** – one persistent `Test_Report_<Bench>.xlsx` per bench in `Logs\Reports`; a row is appended per PASS/FAIL, retests add rows.
- **S3 upload** – after a full cycle the report is uploaded in the background under the meter-type (3PLTCT / 3PWC), bench and date folder; the local file is removed on success.
- **Calibration types** – `single_point` (coefficients within 0–1, no FinalPhAngle columns) or `multi_point` (per-coefficient min/max, incl. FinalPhAngle R/Y/B).
- **SIM ICCID read** – controlled by `sim_fetch_count` (see below).
- **DLMS handling** – `old_dlms` runs the external activation tool; `new_dlms` hides the DLMS button/column.
- **Debug logging** – logs in `Logs\`, toggled by `DEBUG_LOG_ENABLE`.

## Project structure

```
SINGLE_UI/
├── main.py                  # Application entry point (PyQt5 UI)
├── config.json              # Plain bench settings (editable)
├── config_file.enc          # Encrypted, checksum-protected test parameters
├── requirements.txt
├── utility/
│   ├── config.py            # Config loader / decryptor / checksum verifier
│   ├── communication.py     # Serial communication helpers
│   └── ui_logger.py         # Logger setup
└── scripts/
    ├── Test_cases_verificationClass.py
    ├── check_com/           # Check Ports
    ├── calibration/         # Calibration (Phase & Neutral)
    ├── rtt/                 # RTT, IMG, GPRS, RF, Wirepas provisioning
    ├── mct/                 # MCT test
    └── dlms/                # DLMS_ACTIVATION_TOOL_FOR_BENCH_V_1.21.exe + config.json
```

## Setup

Requires Python 3.12 on Windows.

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

`gp_node` (Wirepas) must be installed separately.

## Configuration

`config.json`, `config_file.enc` and the `scripts` (and `assets`) folders must sit **next to the executable / `main.py`**. They are read from there at start-up.

### 1. `config.json` – bench settings (plain text)

| Parameter | Example | Description |
|---|---|---|
| `com_ports` | `["COM6", "COM7", ...]` | COM ports to test. Each port becomes one row in the tables. |
| `DLMS_DONGLE_PORTS` | `[3, 4]` | Dongle port numbers used by the DLMS test. |
| `bench_number` | `"3"` | Bench ID shown in title/header; used in report name and S3 path. |

### 2. `config_file.enc` – test parameters (encrypted)

Encrypted (Fernet, PBKDF2-HMAC-SHA256) and checksum-verified, so it **cannot be edited by hand**; a wrong or modified file is rejected at start-up. Decryption is implemented in `utility/config.py` (`Config.check_encrypted_json`). Keys and credentials are intentionally not listed here. Values below are those of the release package.

**General and project**

| Parameter | Value | Description |
|---|---|---|
| `SELECTED_METER_TYPE` | `3P` | Meter family the config is built for. |
| `SELECTED_TOOL_TYPE` | `SINGLE_UI` | Tool the config is built for. |
| `METER_TYPE` | `3PWC` | Selects the S3 folder (contains "ltct" → 3PLTCT, else 3PWC). |
| `TOOL_TYPE` | `4G` | Communication mode, shown as "Meter Type" in the header and passed to every test. |
| `PROJECT` | `wb` | Project name in the header. |
| `LIVE_VERSION` | `8003` | Live firmware version in the header. |
| `INTERNAL_VERSION` | `3001` | Internal firmware version in the header. |
| `DEBUG_LOG_ENABLE` | `True` | Enables detailed debug logging. |

**Communication and serial numbers**

| Parameter | Value | Description |
|---|---|---|
| `BAUDRATE` | `9600` | Serial baud rate. |
| `SERIAL_TIMEOUT` | `3` | Serial read timeout. |
| `RETRIES` | `4` | Retry count for meter commands. |
| `MAIN_PCB_SFG_PREFIX` | `3P00001` | Expected main PCB serial prefix (Check Ports). |
| `NIC_PCB_SFG_PREFIX` | `0000129` | Expected NIC PCB serial prefix. |
| `NIC_PCB_LENGTH` | `27` | Expected NIC PCB serial length. |

**Calibration**

| Parameter | Value | Description |
|---|---|---|
| `CALIB_TYPE` | `single_point` | `single_point` or `multi_point`; used by Calibration and MCT (also changes Excel log columns). |
| `Phase_before_bench_stab_time` | `30` | Stabilisation wait (s) before Phase calibration. |
| `Phase_after_bench_stab_time` | `40` | Stabilisation wait (s) after Phase calibration. |
| `Neutral_before_bench_stab_time` | `30` | Stabilisation wait (s) before Neutral calibration. |
| `Neutral_after_bench_stab_time` | `40` | Stabilisation wait (s) after Neutral calibration. |
| `PAYMENT_MODE_SET` / `PAYMENT_MODE` | `True` / `1` | Payment mode setting for the meter. |

**RTT, DLMS and MCT**

| Parameter | Value | Description |
|---|---|---|
| `RTT_TIME` | `600` | RTT test duration (s). |
| `DLMS_TYPE` | `old_dlms` | `old_dlms` runs the external DLMS tool; `new_dlms` hides DLMS from UI and reports. |
| `IS_DATA_CONN` | `0` | Data-connection flag for Calibration, RTT, IMG and MCT tests. |
| `sim_fetch_count` | `1` | `1`: read active SIM ICCID only (pass if at least one read and they differ, else toggle SIM and re-read). Any other value (e.g. `2`): active and inactive ICCIDs must both be read, non-zero and different. |
| `Sim_Toggle_Time` | `150` | SIM toggle wait (s) in MCT. |
| `thread_timeout` / `thread_delay` | `300` / `10` | Timeout and delay (s) for the IMG test. |
| `gprs_test_retry` | `2` | Retry count of the GPRS test. |
| `rf_rx_rssi_dbm` / `rf_tx_rssi_dbm` | `-80` / `-80` | RF RX/TX RSSI limits (dBm). |

**Network and SIM**

| Parameter | Value | Description |
|---|---|---|
| `test_router_address` | `2` | Router address used in the RF test. |
| `network_address` | `0x222222` | Wirepas network address (provisioning and RF test). |
| `network_channel` | `2` | Wirepas network channel. |
| `encryption_key` | `********` | Network encryption key (masked). |
| `authentication_key` | `********` | Network authentication key (masked). |
| `sim1_*` / `sim2_*` | empty | SIM 1/2 `user`, `pwd`, `apn`, `pin`, `puk`; currently blank. |

### 3. `scripts/dlms/config.json` – DLMS tool settings

Read by the external DLMS tool (only when `DLMS_TYPE = old_dlms`):

```json
{ "port_list1": [19], "port_list2": [1], "dongle1": 3, "dongle2": 4 }
```

### `utility/config.py` placeholders

`Config.PASSWORD` and `Config.CHECKSUMPASS` contain placeholders (`PUT_ENC_PASSWORD`, `PUT_CHECKSUM_PASSWORD`). Set the real values before use; never commit them.

## Important – before deploying

1. **Keep config files next to the executable** – `config.json`, `config_file.enc`, `assets` and `scripts`.
2. **Set `DLMS_TYPE` correctly** – `new_dlms` for firmware with built-in DLMS, `old_dlms` otherwise.
3. **Do not move or rename the DLMS executable** – `scripts/dlms/DLMS_ACTIVATION_TOOL_FOR_BENCH_V_1.21.exe` and its `config.json` are wired to this exact path.
4. **Check Meter Type and Project** – `METER_TYPE` decides the S3 folder; `PROJECT`, `LIVE_VERSION`, `INTERNAL_VERSION` appear in the header. Verify against the batch being tested.

## Reference

See `Release_Notes_Production_Tool_Bench_3PH_V3_0.docx` for the full release notes.
