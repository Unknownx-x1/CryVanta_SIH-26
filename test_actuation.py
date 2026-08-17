from actuation import create_actuation_command


command = create_actuation_command(
    zone_id=2,
    action="COOLING_ON_SERVO_OPEN"
)

print(command)