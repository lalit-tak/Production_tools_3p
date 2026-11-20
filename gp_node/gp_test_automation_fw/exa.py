


procedure_key={"get_data"
				'bundle_key':{
							'voltage':{
									'index':3,
									'data_byte':4
									},
							'current':{
									'index':3,
									'data_byte':4

									}
							}
				}
if __name__ == '__main__':
	index=2
	data_byte=3
	bundle_key=
	if bundle_key==procedure_key['bundle_key']['voltage']:
		print index
		print data_byte
	if bundle_key==procedure_key['bundle_key']['current']:
		print index
		print data_byte
	