import re
import zipfile

jar = r"C:\Users\italo\Documents\KiCad\10.0\3rdparty\plugins\app_freerouting_kicad-plugin\jar\freerouting-2.2.4.jar"
z = zipfile.ZipFile(jar)
targets = [n for n in z.namelist() if "freerouting" in n.lower() and n.endswith(".class")]
print("classes freerouting:", len(targets))

interesting = [
    n
    for n in targets
    if any(k in n for k in ("CommandLine", "Argument", "Headless", "MainApp", "Graphical", "App"))
]
print("=== classes relevantes ===")
for n in interesting:
    print("  ", n)

pat = re.compile(rb"-[a-zA-Z]{1,5}")
found = {}
for n in interesting:
    try:
        data = z.read(n)
    except Exception:
        continue
    for m in pat.findall(data):
        s = m.decode("ascii", "ignore")
        found.setdefault(s, set()).add(n.split("/")[-1])

print()
print("=== opcoes candidatas ===")
for k in sorted(found):
    print("  %-8s %s" % (k, sorted(found[k])[:3]))

print()
print("=== strings de help em BasicCommandLineArguments ===")
for n in targets:
    if "BasicCommandLine" in n:
        data = z.read(n)
        for m in re.finditer(rb"[\x20-\x7e]{8,90}", data):
            s = m.group().decode("ascii", "ignore")
            if any(w in s.lower() for w in ("gui", "headless", "pass", "design", "output", "help", "usage", "argument")):
                print("   ", s)
