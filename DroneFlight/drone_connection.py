from Mavlink import DroneConnection


if __name__ == "__main__":
    # Устанавливает соединение.
    # Записывает полную информацию о состоянии дрона в файл.
    # 4 Linux or other OS's.
    # connection  = DroneConnection("udpin:localhost:14551")
    # 4 Windows like OS's
    connection  = DroneConnection()
    connection.arm()
    with open('DroneConnectionInfo.json', 'wt') as output_file:
        print(connection.get_mav_state_str(), file=output_file)
