eng.verify_metering_data(voltage = "in range,240000,250000", current = "=,240000")

def verify_metering_data(voltage = "in range,240000,250000", current = "=,240000")
	
	a = {}
	if voltage != False:
		a = int_to_value(voltage)	
		dsdfsdaf
		result_case(a["operator"], b["min_val"], b["max_val"])
		pass fail
	if current != False:
		a = int_to_value(current)	
		result_case(a["operator"], b["min_val"], b["max_val"])
		pass fail
		


def int_to_value(string)
	b = {}

	b["operator"] = string.split(",")[0]
	b["min_val"] = int(string.split(",")[1])
	b["max_val"] = int(string.split(",")[1])
	return b