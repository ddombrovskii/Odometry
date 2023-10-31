from Mavlink import DroneConnection
import time

if __name__ == "__main__":
    # Устанавливает соединение.
    # Взлетает.
    # Висит минут.
    # Садится.
    # 4 Linux or other OS's.
    # connection  = DroneConnection("udpin:localhost:14551")
    # 4 Windows like OS's
    connection  = DroneConnection()
    connection.arm()
    connection.takeoff(4.0)
    time.sleep(60.0)
    connection.land()
    connection.disarm()
