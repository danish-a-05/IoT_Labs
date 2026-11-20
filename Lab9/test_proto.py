# Sanity check on the Pi 5 (normal Python, not the Pico).
# Run after: protoc --python_out=. temperature.proto
import temperature_pb2

msg = temperature_pb2.Reading()
msg.publisher_id = 1
msg.temperature = 21.5
msg.time.hour = 14
msg.time.minute = 30
msg.time.second = 5

data = msg.SerializeToString()
print("Encoded bytes:", data)

decoded = temperature_pb2.Reading()
decoded.ParseFromString(data)
print("Decoded:")
print(decoded)
