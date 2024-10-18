from packaging.version import Version, InvalidVersion


def latest_version(versions):
    valid_versions = []

    for version in versions:
        try:
            valid_versions.append(Version(version))
        except InvalidVersion:
            print(f"Invalid version encountered: {version}")
            continue

    if not valid_versions:
        return None

    return str(max(valid_versions))
