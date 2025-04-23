import threading


def get_last_target(delay: int = 1000):
    def delayed_last():
        Target.WaitForTarget(delay, True)
        Target.Last()
    daemon_thread = threading.Thread(target=delayed_last)
    daemon_thread.daemon = True
    daemon_thread.start()
    res = Target.PromptGroundTarget("")
    daemon_thread.join()
    return res


while Player.Connected:
    Journal.Clear()
    Journal.WaitJournal("There's not enough wood here to harvest.", 60000)
    res = get_last_target()
    print(res)