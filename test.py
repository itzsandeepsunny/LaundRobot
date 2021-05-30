from datetime import datetime,timezone

dat = datetime(2021, 5, 30, 12, 0, 0)
final = (datetime.now() - dat).total_seconds()

print(int(final))

print(datetime.now(timezone.utc))