from Mavlink import DroneConnection
import time


if __name__ == "__main__":
    # Устанавливает соединение.
    # arm.
    # Записывает полную информацию о состоянии дрона в файл.
    # Ожидает минуту.
    # disarm.
    # 4 Linux or other OS's.
    # connection  = DroneConnection("udpin:localhost:14551")
    # 4 Windows like OS's
    connection  = DroneConnection()
    connection.arm()
    with open('DroneArmState.json', 'wt') as output_file:
        print(connection.get_mav_state_str(), file=output_file)
    time.sleep(60)
    connection.disarm()
