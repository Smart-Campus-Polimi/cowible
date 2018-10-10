def change_of_n(mac_address, n):
	new_mac  = ''
	for i in range(0,len(mac_address),3):
		#conversion in int, sum 1 and back in hex
		digits =  hex(int(mac_address[i:i+2],16) + n)
		
		#check if the hex number is less than 0 
		if '-' in digits:
			digits = digits[3:]
			digits = hex(256 - int(digits, 16))

		#check if ff exceed
		if int(digits,16) > 255:
			digits = hex(00 + n)

		#check if there is only one digit
		if len(digits[2:]) < 2:
			digits = '0x0' + digits[2:]		

		new_mac += ':' + digits[2:]
	
	return new_mac[1:]

def generate_possible_siblings(mac_address):
	siblings = []
	for i in range(-10, 0) + range(1,11):
		siblings.append(change_of_n(mac_address, i))

	return siblings