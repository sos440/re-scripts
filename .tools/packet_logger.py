from datetime import datetime

str_now = datetime.now().strftime("%Y%m%d-%H%M%S")

PacketLogger.Start(f"./Data/Packets/{str_now}.txt", False)
Misc.Pause(60000)
PacketLogger.Stop()
Misc.SendMessage("Done!")