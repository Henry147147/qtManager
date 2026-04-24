"""Handles the scanning, renaming of files, extraction of rar and any other file operation"""
from unrar import rarfile

if __name__ == "__main__":
    file = rarfile("../my_archive.part01.rar")
    file.testrar()