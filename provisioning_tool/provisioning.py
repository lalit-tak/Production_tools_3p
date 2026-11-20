# Copyright 2024 Wirepas Ltd licensed under Apache License, Version 2.0
#
# See file LICENSE for full license details.
#

import argparse
import functools
import queue
import logging
from provisioning_tool import wirepas_provisioning
import sys
from provisioning_tool import factory_mode
from time import sleep
import cbor2

from provisioning_tool.wirepas_provisioning import WirepasProvisioning

PROVISIONING_CLEAR_MAGIC = 0x45238176

class Communication:
    DRY_RUN_RECEIVE_TIMEOUT_S = 2
    READ_PARAMETERS_TIMEOUT_S = 2
    APPLY_RECEIVE_TIMEOUT_S = 2
    STOP_FACTORY_MODE_TIMEOUT_S = 2

    def __init__(self):
        # NOTE: these used to be class attributes shared through a single
        # module-level `nic_com = Communication()` singleton. That's why
        # provisioning a single meter worked fine, but provisioning several
        # meters at once (one thread per COM port) failed: every thread's
        # serial_initialization() call shared the same fm/serial
        # connection/rx thread, and responses from different meters landed
        # in the same result queues. Instance attributes + a fresh
        # Communication() per provisioning call give each concurrent call
        # its own isolated state.
        self.fm = factory_mode.FactoryMode()

        self.provisioning_success_queue = queue.Queue()
        self.read_parameters_queue = queue.Queue()
        self.apply_success_queue = queue.Queue()
        self.stop_factory_mode_queue = queue.Queue()


def parse_message_received(com: Communication, type: factory_mode.MessageType, data: bytes):
    if type == factory_mode.MessageType.PROVISIONING_WRITE_RESPONSE:
        if wirepas_provisioning.is_provisioning_dry_run_successful(data) is True:
            logging.debug("Dry Run Successful!")
            com.provisioning_success_queue.put(True)
        else:
            logging.debug("Dry Run returned an error!")
            com.provisioning_success_queue.put(False)
    elif type == factory_mode.MessageType.PROVISIONING_APPLY_RESPONSE:
        if wirepas_provisioning.is_provisioning_apply_successful(data) is True:
            logging.debug("Apply Successful!")
            com.apply_success_queue.put(True)
        else:
            logging.debug("Apply returned an error!")
            com.apply_success_queue.put(False)
    elif type == factory_mode.MessageType.PROVISIONING_READ_RESPONSE:
        logging.debug("Read Request Response Received")
        com.read_parameters_queue.put(data)
    elif type == factory_mode.MessageType.STOP_FACTORY_MODE_AND_RESET_RESPONSE:
        logging.debug("Stop Factory Mode and Reset Response Received")
        com.stop_factory_mode_queue.put(True)
    else:
        logging.warning("Unknown type received: %s", type)


def perform_parameters_provisioning(com: Communication, wp_prov: WirepasProvisioning, reboot_time_s: int):
    provisioning_packet = wp_prov.get_provisioning_packet()

    logging.debug(f"Provisioning packet size: {len(provisioning_packet)} bytes")
    logging.debug(f"Provisioning packet hex: {provisioning_packet.hex()}")

    logging.info("Sending Provisioning Packet")
    if (
        factory_mode.send_factory_mode_message(
            com.fm,
            provisioning_packet,
            factory_mode.MessageType.PROVISIONING_WRITE_REQUEST,
        )
        is False
    ):
        factory_mode.error_print_and_exit(
            com.fm,
            "Sending Provisioning Packet isn't successful!",
            factory_mode.ExitCodes.SENDING_FAILED,
        )

    try:
        validation_run_success = com.provisioning_success_queue.get(
            timeout=com.DRY_RUN_RECEIVE_TIMEOUT_S
        )
    except queue.Empty:
        factory_mode.error_print_and_exit(
            com.fm,
            "Provisioning validation run return code not received in the given timeout!",
            factory_mode.ExitCodes.RECEPTION_TIMEOUT,
        )
        return {}, False, "Provisioning validation run timeout"

    if validation_run_success is False:
        factory_mode.error_print_and_exit(
            com.fm,
            "Provisioning validation run was not successful!",
            factory_mode.ExitCodes.INVALID_PARAMETERS,
        )
        return {}, False, "Provisioning validation run failed"

    logging.info("Applying parameters to the NIC")

    if reboot_time_s == 0:
        logging.info("Sending provisioning apply and reboot request")
        if (
            factory_mode.send_factory_mode_message(
                com.fm, bytes(), factory_mode.MessageType.PROVISIONING_REBOOT_REQUEST
            )
            is False
        ):
            factory_mode.error_print_and_exit(
                com.fm,
                "Sending Device Reboot Request not successful!",
                factory_mode.ExitCodes.SENDING_FAILED,
            )
            return {}, False, "Sending reboot request failed"
    else:
        logging.info("Sending apply request (no reboot)")
        if (
            factory_mode.send_factory_mode_message(
                com.fm, bytes(), factory_mode.MessageType.PROVISIONING_APPLY_REQUEST
            )
            is False
        ):
            factory_mode.error_print_and_exit(
                com.fm,
                "Sending Provisioning Apply Request not successful!",
                factory_mode.ExitCodes.SENDING_FAILED,
            )
            return {}, False, "Sending apply request failed"
        
        # Wait for apply response
        try:
            apply_success = com.apply_success_queue.get(
                timeout=com.APPLY_RECEIVE_TIMEOUT_S
            )
        except queue.Empty:
            factory_mode.error_print_and_exit(
                com.fm,
                "Provisioning apply response not received in the given timeout!",
                factory_mode.ExitCodes.RECEPTION_TIMEOUT,
            )
            return {}, False, "Provisioning apply timeout"

        if apply_success is False:
            factory_mode.error_print_and_exit(
                com.fm,
                "Provisioning apply was not successful!",
                factory_mode.ExitCodes.INVALID_PARAMETERS,
            )
            return {}, False, "Provisioning apply failed"
        
        logging.info("Parameters applied successfully without reboot")


def perform_parameters_reading(com: Communication):
    logging.info("Sending request to read NIC Parameters")
    summary = ""
    if (
        factory_mode.send_factory_mode_message(
            com.fm, bytes(), factory_mode.MessageType.PROVISIONING_READ_REQUEST
        )
        is False
    ):
        factory_mode.error_print_and_exit(
            com.fm,
            "Sending Read Parameters Request not successful!",
            factory_mode.ExitCodes.SENDING_FAILED,
        )
        return {}, False, "Sending read parameters request failed"

    try:
        nic_parameters_data = com.read_parameters_queue.get(
            timeout=com.READ_PARAMETERS_TIMEOUT_S
        )
    except queue.Empty:
        factory_mode.error_print_and_exit(
            com.fm,
            "Read Parameters response was not received in the given timeout!",
            factory_mode.ExitCodes.RECEPTION_TIMEOUT,
        )
        return {}, False, "Read parameters timeout"
    nic_parameters_data = wirepas_provisioning.decode_prov_dict(nic_parameters_data)

    summary = wirepas_provisioning.print_provisioning_summary(nic_parameters_data)

    prov_sucess = wirepas_provisioning.get_provisioning_status(nic_parameters_data)

    if prov_sucess is True:
        factory_mode.success_print("NIC is successfully provisioned!")
    else:
        factory_mode.error_print("Missing parameters in the device!")
    return nic_parameters_data, prov_sucess, summary


def perform_parameters_clearing(com: Communication):
    logging.info("Sending request to clear NIC Parameters")
    if (
        factory_mode.send_factory_mode_message(
            com.fm, PROVISIONING_CLEAR_MAGIC.to_bytes(4, byteorder='little'), factory_mode.MessageType.PROVISIONING_CLEAR_REQUEST
        )
        is False
    ):
        factory_mode.error_print_and_exit(
            com.fm,
            "Sending clear NIC Parameters Request not successful!",
            factory_mode.ExitCodes.SENDING_FAILED,
        )
        return {}, False, "Sending clear parameters request failed"
    factory_mode.success_print("NIC Parameters cleared successfully!")


def stop_factory_mode_and_reset(com: Communication, delay_s: int = 0):
    """
    Send command to stop factory mode and reset after specified delay
    
    Args:
        com: Communication object
        delay_s: Delay in seconds before reset (default: 0 for immediate reset)
    """
    logging.info(f"Sending request to stop factory mode and reset in {delay_s} seconds")
    
    # Encode delay as CBOR
    delay_data = cbor2.dumps(delay_s)
    
    if (
        factory_mode.send_factory_mode_message(
            com.fm, delay_data, factory_mode.MessageType.STOP_FACTORY_MODE_AND_RESET
        )
        is False
    ):
        factory_mode.error_print_and_exit(
            com.fm,
            "Sending Stop Factory Mode and Reset request not successful!",
            factory_mode.ExitCodes.SENDING_FAILED,
        )
    
    # Wait for acknowledgment
    try:
        stop_success = com.stop_factory_mode_queue.get(
            timeout=com.STOP_FACTORY_MODE_TIMEOUT_S
        )
    except queue.Empty:
        factory_mode.error_print_and_exit(
            com.fm,
            "Stop Factory Mode and Reset response not received in the given timeout!",
            factory_mode.ExitCodes.RECEPTION_TIMEOUT,
        )
    
    if stop_success:
        if delay_s == 0:
            logging.info("Reponse received. Device will reboot immediately")
        else:
            logging.info(f"Reponse received. Device stopped factory mode and will reset in {delay_s} seconds")
    
    # factory_mode.serial_cleanup(com.fm)


def provision_nic_parameters(args: argparse, com_ser):
    # Managing the communication with the NIC
    # A fresh Communication() per call keeps this thread's serial
    # connection/rx thread/result queues isolated from any other
    # meter being provisioned concurrently on another thread.
    nic_com = Communication()
    nic_parameters_data = {}
    prov_sucess = False
    summary = ""
    nic_com.fm.parse_message_callback = functools.partial(parse_message_received, nic_com)

    factory_mode.serial_initialization(args.serial_port, nic_com.fm, args.baudrate, com_ser)

    logging.info("Starting NIC Provisioning")

    # Get all argument attributes except serial_port, baudrate, reboot_time (which are always set)
    provisioning_params = {
        k: v for k, v in vars(args).items() if k not in ["serial_port", "baudrate", "reboot_time"]
    }

    # Check if all provisioning parameters are None
    if all(value is None for value in provisioning_params.values()):
        logging.error(
            "No parameters specified for provisioning! All parameters are NULL!"
        )
        logging.error("At least one parameter must be specified.")
        factory_mode.serial_cleanup(nic_com.fm)
        sys.exit(factory_mode.ExitCodes.MISSING_PARAMETERS.value)

    # Create WirepasProvisioning object with all parameters from args
    wp_prov = WirepasProvisioning(
        encryption_key=args.encryption_key,
        authentication_key=args.authentication_key,
        network_address=args.network_address,
        network_channel=args.network_channel,
        node_address=args.node_address,
        node_role=args.node_role,
        gw_key_enc_key=args.gw_key_enc_key,
        mtr_auth_key=args.mtr_auth_key,
        mtr_enc_key=args.mtr_enc_key,
        mtr_mr_secret=args.mtr_mr_secret,
        mtr_us_secret=args.mtr_us_secret,
        mtr_fu_secret=args.mtr_fu_secret,
        mtr_baud_rate=args.mtr_baud_rate,
        mtr_dlms_mode=args.mtr_dlms_mode,
        gateway_id=args.gateway_id,
        sink_address=args.sink_address,
        sim1_apn=args.sim1_apn,
        sim1_username=args.sim1_username,
        sim1_password=args.sim1_password,
        sim1_pdp_type=args.sim1_pdp_type,
        sim1_pin=args.sim1_pin,
        sim1_puk=args.sim1_puk,
        sim1_band_lock=args.sim1_band_lock,
        sim2_apn=args.sim2_apn,
        sim2_username=args.sim2_username,
        sim2_password=args.sim2_password,
        sim2_pdp_type=args.sim2_pdp_type,
        sim2_pin=args.sim2_pin,
        sim2_puk=args.sim2_puk,
        sim2_band_lock=args.sim2_band_lock,
        mqtt_hostname=args.mqtt_hostname,
        mqtt_port=args.mqtt_port,
        mqtt_username=args.mqtt_username,
        mqtt_password=args.mqtt_password,
        mqtt_unsecure=args.mqtt_unsecure,
        ntp_addr=args.ntp_addr,
        tz_offset_min=args.tz_offset_min,
        keepalive_intvl_s=args.keepalive_interval,
        reset_hour=args.reset_hour,
        reset_minute=args.reset_minute,
        sim_selection=args.sim_selection,
    )

    # Check if at least one parameter is provided
    if not any(value is not None for value in vars(wp_prov).values()):
        logging.error(
            "No parameters specified for provisioning! All parameters are NULL!"
        )
        logging.error("At least one parameter must be specified.")
        factory_mode.serial_cleanup(nic_com.fm)
        return {}, False, "No valid parameters provided"
        # sys.exit(factory_mode.ExitCodes.MISSING_PARAMETERS.value)

    factory_mode.wait_for_challenge_response_with_reset_loop(nic_com.fm)
    perform_parameters_provisioning(nic_com, wp_prov, args.reboot_time)

    if args.reboot_time == 0:
        logging.info("Waiting for NIC to reboot...")
        # Add delay to allow device to complete reboot
        sleep(2.0)

        # Check if mtr_baud_rate was provisioned and switch baudrate if needed
        if args.mtr_baud_rate is not None:
            factory_mode.switch_baudrate_if_needed(
                nic_com.fm, args.serial_port, args.mtr_baud_rate
            )

        factory_mode.wait_for_challenge_response_with_reset_loop(nic_com.fm)
    
    # Read parameters after provisioning
    nic_parameters_data, prov_sucess, summary = perform_parameters_reading(nic_com)

    # Stop factory mode and reset with specified delay
    stop_factory_mode_and_reset(nic_com, args.reboot_time)
    return nic_parameters_data, prov_sucess, summary

    # sys.exit(factory_mode.ExitCodes.SUCCESS.value)


def read_nic_parameters(args: argparse):
    # Managing the communication with the NIC
    nic_com = Communication()
    nic_com.fm.parse_message_callback = functools.partial(parse_message_received, nic_com)

    factory_mode.serial_initialization(args.serial_port, nic_com.fm, args.baudrate)

    factory_mode.wait_for_challenge_response_with_reset_loop(nic_com.fm)
    perform_parameters_reading(nic_com)

    # Stop factory mode and reset immediately
    stop_factory_mode_and_reset(nic_com)

    sys.exit(factory_mode.ExitCodes.SUCCESS.value)


def clear_nic_parameters(args: argparse):
    # Managing the communication with the NIC
    nic_com = Communication()
    nic_com.fm.parse_message_callback = functools.partial(parse_message_received, nic_com)

    factory_mode.serial_initialization(args.serial_port, nic_com.fm, args.baudrate)

    factory_mode.wait_for_challenge_response_with_reset_loop(nic_com.fm)
    perform_parameters_clearing(nic_com)
    
    # Stop factory mode and reset immediately
    stop_factory_mode_and_reset(nic_com)

    sys.exit(factory_mode.ExitCodes.SUCCESS.value)


if __name__ == "__main__":
    factory_mode.error_print("Unavailable. Please use 'provision_img_parameters.py' or 'read_img_parameters.py'")
    sys.exit(factory_mode.ExitCodes.CALL_TO_MAIN.value)
