Output helm_install.gif

Set FontSize 14
Set Width 1400
Set Height 600

Type "helm repo add srekit https://srekit.github.io/helm-charts"
Sleep 500ms
Enter
Sleep 500ms
Type "helm -n inventory upgrade kube-inventory --install --create-namespace srekit/kube-inventory"
Sleep 500ms
Enter
Sleep 5s
