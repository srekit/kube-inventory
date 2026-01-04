Output csv_format.gif

Set FontSize 14
Set Width 1400
Set Height 600

Type "kube-inventory --output-mode csv"
Sleep 500ms
Enter
Sleep 10s
Type "clear"
Enter
Sleep 500ms
Type "head -n 3 inv_data/inventory.csv | column -s, -t"
Enter
Sleep 5s
