#!/usr/bin/env python
import os, shutil
import zipfile
from datetime import datetime


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def delete(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def backup(filename, currentdir, newdir):
    try:
        dt_string = datetime.now().strftime("%d%m%Y%H%M%S")

        zip_string = filename + dt_string + ".zip"
        zipf = zipfile.ZipFile(zip_string, 'w', zipfile.ZIP_DEFLATED)
        zipdir(currentdir, zipf)
        zipf.close()
        os.rename(zip_string, newdir + zip_string)
    except Exception as e:
        print('Failed to zip %s. Reason: %s' % (zip_string, e))


if __name__ == '__main__':

    backup("reports-backup-", "caliper-reports/", "old/old-reports/")
    delete("caliper-reports/")

    backup("aggregated-backup-", "aggregated-results/", "old/old-aggregated-results/")
    delete("aggregated-results/")
