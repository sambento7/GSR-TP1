from datetime import datetime
import time


#dia:mes:ano:hora:minuto:segundo:milissegundo
def gerar_timestamp_data() -> str:
    currentDate = datetime.now().month

    print("current date" + str(currentDate))
    date = datetime.now().strftime(f"%d:%m:%Y:%H:%M:%S:{int(time.time() * 1000) % 1000:03d}")
    print("data " + str(date))
    return date
