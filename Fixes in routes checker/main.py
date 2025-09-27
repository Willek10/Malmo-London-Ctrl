import re


def clearFixes(filename):
    fixes = set()
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            fix_match = re.match(r"(\w{2}\d{3}|\w{5}|\w{3})", line)
            if fix_match:
                fixes.add(fix_match.group(1))
    return fixes


def parseAirways(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    blocks = content.split("RTE")
    airways_dict  = {}

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        route_match = re.match(r"(\w{1,3}\d{1,3})", block)
        if route_match:
            route_name = route_match.group(1)
        else:
            continue

        fixes = re.findall(r"FIX\s+(\w+)", block)
        airways_dict[route_name] = fixes

    return airways_dict


def checkFixInAirway(airways, fixes_set):
    reported = set()
    notExist = []
    for route, route_fixes in airways.items():
        for fix in route_fixes:
            if fix not in fixes_set and fix not in reported:
                reported.add(fix)
                notExist.append(f"{fix} does not exist in fixes.txt")
    notExist.sort()

    with open("output.txt", "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("------------ Fixes in airways ------------\n")
        for item in notExist:
            f.write(f"{item}\n")


def parseCoded(filename):
    routes = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            routes_match = re.search(r"([A-Z*]{4}\.\w{5}\.|\w{3}\.|\w{1,2}\.\d{1,3})(.*)$", line)
            if routes_match:
                routes.append(f"{routes_match.group(1)}{routes_match.group(2)}")
    return routes


def checkFixesInCoded(coded_routes, fixes_set):
    missing = []
    reported = set()

    for route in coded_routes:
        parts = route.split(".")
        for fix in parts:
            if not fix:
                continue
            if re.match(r"^[A-Z]\d+", fix):
                continue
            if re.match(r"^[A-Z]{4}$", fix):
                continue
            if "*" in fix:
                continue

            if fix not in fixes_set and fix not in reported:
                reported.add(fix)
                missing.append(f"{fix} does not exist in fixes.txt")

    missing.sort()

    with open("output.txt", "a", encoding="utf-8") as f:
        f.write("------------ Missing fixes in coded.ini ------------\n")
        for m in missing:
            f.write(m + "\n")


def checkAirwaysInCoded(coded_routes, airways_dict, fixes_set):
    missing = []
    reported = set()
    fixes_set_upper = {fix.upper() for fix in fixes_set}

    for route in coded_routes:
        parts = route.split(".")
        
        for i in range(len(parts) - 2):
            if (re.match(r"^[A-Z]\d+$", parts[i+1]) and parts[i+1] in airways_dict):
                
                airway_name = parts[i+1]
                start_fix = parts[i]
                end_fix = parts[i+2]
                
                airway_fixes = airways_dict[airway_name]
                
                try:
                    start_index = airway_fixes.index(start_fix)
                    end_index = airway_fixes.index(end_fix)
                except ValueError:
                    missing.append(f"ERROR: {start_fix} or {end_fix} not found in airway {airway_name}")
                    continue
                
                if start_index < end_index:
                    segment = airway_fixes[start_index:end_index + 1]
                else:
                    segment = airway_fixes[end_index:start_index + 1]
                    segment.reverse()
                
                for fix in segment:
                    if fix not in fixes_set_upper and fix not in reported:
                        reported.add(fix)
                        missing.append(f"{fix} (via {airway_name}) does not exist in fixes.txt")
    
    missing.sort()
    with open("output.txt", "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("------------ Missing airway expansions in coded.txt ------------\n")
        for m in missing:
            f.write(m + "\n")


def main():
    fixes_set = clearFixes("fixes.txt")
    airways = parseAirways("airways.txt")
    coded = parseCoded("coded.txt")
    checkFixesInCoded(coded, fixes_set)
    checkFixInAirway(airways, fixes_set)
    checkAirwaysInCoded(coded, airways, fixes_set)


if __name__ == "__main__":
    main()
