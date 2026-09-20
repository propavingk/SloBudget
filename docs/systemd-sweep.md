# Recipe: a systemd timer for a budget sweep

Run the alert evaluation on a schedule and keep the output as a log of what
the paging system should have done.

## The unit files

`/etc/systemd/system/slo-sweep.service`:

```ini
[Unit]
Description=SLO budget sweep

[Service]
Type=oneshot
WorkingDirectory=/opt/slo
ExecStart=/usr/bin/python3 -m slobudget alerts service-a.sli --objective 99.9 --window 30d --json
SuccessExitStatus=0 1
```

`SuccessExitStatus=0 1` treats an alert finding as a successful run. The
signal worth reading is the report line, not the unit state.

`/etc/systemd/system/slo-sweep.timer`:

```ini
[Unit]
Description=Hourly budget sweep

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Enable with `systemctl enable --now slo-sweep.timer`.
