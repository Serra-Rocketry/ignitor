import zipfile, re
jar = r"C:\Users\italo\Documents\KiCad\10.0\3rdparty\plugins\app_freerouting_kicad-plugin\jar\freerouting-2.2.4.jar"
z = zipfile.ZipFile(jar)
names = [n for n in z.namelist() if n.endswith(".class")]
pat = re.compile(rb"(?:-{1,2}[a-z][a-z0-9_-]{1,24})")
found = {}
for n in names:
    if "cli" not in n.lower() and "Arg" not in n and "MainApp" not in n and "Main" not in n:
        continue
    try:
        data = z.read(n)
    except Exception:
        continue
    for m in pat.findall(data):
        s = m.decode("ascii", "ignore")
        if len(s) >= 2:
            found.setdefault(s, set()).add(n.split("/")[-1])
for k in sorted(found):
    if k.startswith("-"):
        print("%-22s %s" % (k, sorted(found[k])[:2]))
