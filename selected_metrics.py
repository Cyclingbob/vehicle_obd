from config import watched_metrics_file

def getWatchedMetrics():
    contents = open(watched_metrics_file, "r").read()
    metrics = contents.split("\n")
    return metrics
