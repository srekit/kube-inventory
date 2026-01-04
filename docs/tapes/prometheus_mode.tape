Output prometheus_mode.gif

Set FontSize 14
Set Width 1400
Set Height 600

Type "kube-inventory --output-mode prometheus &"
Sleep 500ms
Enter
Sleep 10s
Type "clear"
Enter
Sleep 500ms
Type "curl -s localhost:8080/metrics | head -n 5"
Sleep 500ms
Enter
Sleep 5s
