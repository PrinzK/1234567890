import sender

if sender.send_message(5001, "hello") == "message: 'hello' sent":
	print "testing sender function send_message(port, message) successful"
else: 
	print "testing sender function send_message(port, message) NOT successful"
