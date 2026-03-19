def save_file(content, filename):
    with open(filename, "w") as f:
        f.write(content)
    return filename