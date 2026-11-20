import ftt_merger_tool
from provisioning_tool.communication import Communication
import subprocess
from multiprocessing import Process, Queue, freeze_support
import logging
import json
import re
import tkinter as tk
from tkinter import scrolledtext
from tkinter import font
from colorama import Fore, Style, init
from config import Config
import time
from text_logging import setup_logger
setup_logger(enable_file_log=True)
init(autoreset=True)

# ---------------- GUI ----------------
def show_summary_all(results, toolname):
    root = tk.Tk()
    if toolname == 'img':
        root.title("IMG MCT + FTT + Provisioning Summary")
    else:
        root.title("FTT Summary")

    # Window size
    w, h = 900, 600
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.resizable(False, False)

    tk.Label(root, text="SUMMARY", font=("Arial", 20, "bold")).pack(pady=10)

    # ---------- MAIN CONTAINER ----------
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # ---------- TEXT FRAME ----------
    text_frame = tk.Frame(main_frame)
    text_frame.pack(fill="both", expand=True, padx=20)

    text = scrolledtext.ScrolledText(
        text_frame,
        width=110,
        height=20,
        font=("Courier New", 12)
    )
    text.pack(fill="both", expand=True)

    # ---------- DEFINE FONTS & TAGS ----------
    bold_font = font.Font(text, text.cget("font"))
    bold_font.configure(weight="bold")

    text.tag_configure("bold", font=bold_font)
    text.tag_configure("overall_pass", foreground="green", font=bold_font)
    text.tag_configure("overall_fail", foreground="red", font=bold_font)

    # ---------- BUTTON ----------
    btn_frame = tk.Frame(root)
    btn_frame.pack(fill="x", pady=10)

    tk.Button(
        btn_frame,
        text="OK",
        font=("Arial", 16, "bold"),
        command=root.destroy
    ).pack()

    # ---------- results is a dict keyed by com port ----------
    records = results.values()

    if 'img' in toolname.lower():
        for r in records:
            # Section header
            text.insert(
                tk.END,
                f"\n{'=' * 20} {r['com_port']} {'=' * 20}\n",
                "bold"
            )
            mct = r["mct"].upper()
            ftt = r["ftt"].upper()
            prov = r["prov"].upper()
            overall = r["overall"].upper()

            # MCT
            text.insert(tk.END, "MCT          : ")
            text.insert(tk.END, f"{mct}\n")
            if mct == "FAIL":
                text.insert(tk.END, f"MCT Reason   : {r.get('mct_reason', '')}\n")

            # FTT
            text.insert(tk.END, "FTT          : ")
            text.insert(tk.END, f"{ftt}\n")
            if ftt == "FAIL":
                text.insert(tk.END, f"FTT Reason   : {r.get('ftt_reason', '')}\n")

            # Provisioning
            text.insert(tk.END, "Provisioning : ")
            text.insert(tk.END, f"{prov}\n")
            if prov == "FAIL":
                text.insert(tk.END, f"Prov Reason  : {r.get('prov_reason', '')}\n")

            # Overall (colored)
            text.insert(tk.END, "Overall      : ", "bold")
            if overall.lower() == "pass":
                text.insert(tk.END, f"{overall}\n", "overall_pass")
            else:
                text.insert(tk.END, f"{overall}\n", "overall_fail")
    else:      
        for r in records:
            # Section header
            text.insert(
                tk.END,
                f"\n{'=' * 20} {r['com_port']} {'=' * 20}\n",
                "bold"
            )


            mct = r["mct"].upper()
            ftt = r["ftt"].upper()
            overall = r["overall"].upper()

            # MCT
            text.insert(tk.END, "MCT          : ")
            text.insert(tk.END, f"{mct}\n")
            if mct == "FAIL":
                text.insert(tk.END, f"MCT Reason   : {r.get('mct_reason', '')}\n")

            # FTT
            text.insert(tk.END, "FTT          : ")
            text.insert(tk.END, f"{ftt}\n")
            if ftt == "FAIL":
                text.insert(tk.END, f"FTT Reason   : {r.get('ftt_reason', '')}\n")

            # Overall (colored)
            text.insert(tk.END, "Overall      : ", "bold")
            if overall.lower() == "pass":
                text.insert(tk.END, f"{overall}\n", "overall_pass")
            else:
                text.insert(tk.END, f"{overall}\n", "overall_fail")

    text.config(state="disabled")
    root.mainloop()

# ---------------- UTIL ----------------
def load_json_with_comments(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'#.*', '', content)
    return json.loads(content)

# ---------------- PCB SERIAL ----------------
def get_pcb_serial(port, meter_type):
    print(f"Reading PCB Serial from {port}...")
    com = Communication(port)
    try:
        com.open()

        body = bytes([
            0xaa, 0x1, 0x4e, 0x47, 0xc9,
            0xff, 0xff, 0xff, 0xff,
            0x4, 0x4, 0x8, 0xc7, 0x52, 0x0,
            0x0, 0xc, 0x7, 0x0, 0x1e, 0xae, 0x8d
        ])

        com.send_data(body, expected_payload_len=2)
        resp = com.read_response(timeout=5)
        serial = resp[12:39].replace(b'\x00', b'').decode()
        return serial
    except Exception as e:
        logging.error(f"{port}: PCB read error {e}")
        return None
    finally:
        com.close()

# ---------------- FTT ----------------
def run_ftt_sequential(com_port_list, serial_cfg, cpu_serial_num, results):
    ftt_res = ftt_merger_tool.run(com_port_list, results, serial_cfg, cpu_serial_num)
    for com in com_port_list:
        r = ftt_res.get(com.lower()) or {}
        results[com.lower()]["ftt"] = r.get("result", "fail")
        results[com.lower()]['ftt_reason'] = r.get("msg", "")
        # COM port / MCT checks now run inside ftt_merger_tool.main_function
        for key in ("mct", "mct_reason", "prov", "prov_reason"):
            if key in r and (key.startswith("mct") or "prov" in results[com.lower()]):
                results[com.lower()][key] = r[key]
    return results

# Getting serial number from powershell
def get_bios_serial():
    try:
        result = subprocess.check_output(
            [
                "powershell",
                "-Command",
                "Get-CimInstance Win32_BIOS | Select-Object -ExpandProperty SerialNumber"
            ],
            stderr=subprocess.STDOUT,
            text=True
        )

        serial = result.strip()

        if serial:
            return serial
        else:
            return "1111111111"

    except subprocess.CalledProcessError as e:
        print("Error:", e)
        logging.error(f"Error in getting bios serial number: {str(e)}")
        return "1111111111"


# ---------------- MAIN ----------------
def run_main(port_list, data_dict):
    com_port_list_main = port_list.get("com_port", [])
    com_port_list = []
    for com_port in com_port_list_main:
        if com_port:
            com_port_list.append(f"COM{com_port}")
    cpu_serial_num = get_bios_serial()
    print(f"CPU Serial number: {cpu_serial_num}")
    logging.info(f"CPU Serial number: {cpu_serial_num}")
    # i = 0
    while True:
        input("Press Enter to Start the tool.......")
        logging.info("\nStart new the tool.......")
        is_img = 'img' in data_dict.get('TOOL_TYPE', 'img_ftt').lower()
        summary_type = 'img' if is_img else '4g'

        if not com_port_list:
            no_port = {
                "com_port": "COM Port is not selected",
                "mct": "fail", "mct_reason": "",
                "ftt": "fail", "ftt_reason": "",
                "prov": "fail", "prov_reason": "",
                "overall": "fail",
            }
            show_summary_all({"none": no_port}, summary_type)
        else:
            # Default results, keyed by lower-case com port
            results = {}
            for com_port in com_port_list:
                entry = {
                    "com_port": com_port,
                    "mct": "fail", "mct_reason": "",
                    "ftt": "fail", "ftt_reason": "MCT NOT PASSED",
                    "overall": "fail",
                }
                if is_img:
                    entry["prov"] = "fail"
                    entry["prov_reason"] = "FTT NOT PASSED"
                results[com_port.lower()] = entry

            # STAGE 1: COM port check -> PCB serial -> MCT -> FTT -> IMG provisioning,
            # all done per port inside ftt_merger_tool.main_function
            run_ftt_sequential(com_port_list, data_dict, cpu_serial_num, results)
            print(results)

            # STAGE 2: overall
            stages = ("mct", "ftt") + (("prov",) if is_img else ())
            for r in results.values():
                r["overall"] = "pass" if all(r[s].lower() == "pass" for s in stages) else "fail"
            logging.info(f"Final Results: {results}")

            show_summary_all(results, summary_type)

            # input("\nPress Enter to start 3P LTCT/WC FTT + IMG PROVISIONING V3.0.1.0 ...\n")


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    cfg = Config()
    port_json = {}
    port_status = False
    serial_config = {}
    serial_config_status = False
    print(Fore.GREEN + "Loading Configurations...")
    port_json, port_status = cfg.load_config_json('config.json')
    if not port_status:
        print(Fore.RED + "Com Port is not available in config...")
    else:
        print(Fore.GREEN + "Com port is loaded...")
        print(Fore.GREEN + "Used Com Port: " + Fore.YELLOW + f"{port_json}")
        serial_config, serial_config_status = cfg.check_encrypted_json('config_file.enc')
        # serial_config['TOOL_TYPE'] = '4g_ftt'
        if serial_config_status:
            print(Fore.GREEN + "Configuration Parameters is Loaded...")
            print(Fore.GREEN + "Used Configuration: " + Fore.YELLOW + f"{serial_config}")
            print(Fore.GREEN + Style.RESET_ALL)
            print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<...............3P LTCT/WC FTT + IMG(3.2.7) PROVISIONING V3.0.1.8 .....................>>>>>>>>>>>>>>>>>>>")
            
            run_main(port_json, serial_config)
        else:
            print(Fore.RED + "Fixed Serial config is currepted")
            time.sleep(2)
    print("Closing FTT Tool..")
    time.sleep(3)
    