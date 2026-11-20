import time
from procedure import procedure_keys_sent
from engine import procedure_keys
# from 1p import rx_byte_array


if __name__ == "__main__":


	start = procedure_keys_sent()
	# start.eng.set_time("now")
	# start.default_relay()
	# start.verify_relay_control()
	# start.power_limit_test()
	# start.verify_high_load()
	# start.cover_openInManual()
	# start.cover_openInAuto()
	# start.relay_withNegativeCredit()
	# start.eng.factory_init2()


	## three phase.
	# try:
	# 	start.default_threerelay()
	# except Exception as err:
	# 	print err
	# 	pass
	# try:
	# 	start.relay_afterFactoryInit()
	# except Exception as err:
	# 	print err
	# 	pass
	# try:
	# 	start.verify_relay_control()
	# except Exception as err:
	# 	print err
	# 	pass
	# try:
	# 	start.power_limit_test()
	# except Exception as err:
	# 	print err
	# 	pass
	# try:
	# 	start.verify_high_load()
	# except Exception as err:
	# 	if err =='TIMEOUT_START_BYTE':
	# 		start.dlms_tap()
	# 	pass

	# try:
	# 	start.relay_withNegativeCredit()
	# except Exception as err:
	# 	if err =='TIMEOUT_START_BYTE':
	# 		start.dlms_tap()
	# 	pass
	# try:
	# 	start.cover_openInManual()
	# except Exception as err:
	# 	if err =='TIMEOUT_START_BYTE':
	# 		start.dlms_tap()
	# 	pass
	# try:
	# 	start.cover_openInAuto()
	# except Exception as err:
	# 	if err =='TIMEOUT_START_BYTE':
	# 		start.dlms_tap()
	# 	pass
	# try:
	# 	start.high_loadWith_c_open()
	# except Exception as err:
	# 	if err =='TIMEOUT_START_BYTE':
	# 		start.dlms_tap()
	# 	pass
	try:
		start.high_loadWith_prepaid()
	except Exception as err:
		if err =='TIMEOUT_START_BYTE':
			start.dlms_tap()
		pass











	# start.eng.startcase()
	# start.eng.dlms_tap()
	# start.factory_reset()
	# start.case_01_default_parameter()
	# start.case_02_enable_disable_parameter()
	# start.case_03_recharge_parameter()
	# start.case_04_eg_parameter()
	# start.case_05_dg_parameter()
	# start.case_06_set_eg_dg_parameter()
	# start.case_07_recharge_with_eg_dg()
	# start.case_08_set_eg_deduction_parameter()
	# start.case_09_eg_one_month_deduction()
	# start.case_10_eg_two_month_deduction()
	# start.case_11_eg_with_year_deduction()
	# start.case_12_eg_leap_to_nonleap_deduction()
