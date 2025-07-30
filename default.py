import urllib2
import json
import os
import xbmcgui
import xbmc
import time
import re
import xbmcaddon
import xbmcplugin

addon = xbmcaddon.Addon('script.cuteShop')
ROOT_URL = ""
API_URL = ""
FILE_URL = ""
BOXART_URL = "https://mobcat.zip/XboxIDs/title.php?{}&thumbnail=xbmc"
ATTACHER_URL = "http://mobcat.zip/attacher/?XMID={}&download"
DOWNLOAD_DIRECTORY = addon.getSetting('DOWNLOAD_DIRECTORY')

def sanitize_for_fatx(filename):
    invalid_chars = r'[\\/:*?"<>|+,;=\[\]]'
    filename = re.sub(invalid_chars, ' ', filename)

    filename = filename.rstrip('. ')

    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        max_name_length = 42 - len(ext) - 1  # account for dot
        name = name[:max_name_length]
        filename = name + '.' + ext
    else:
        filename = filename[:42]

    return filename

def get_user_code():
    kb = xbmc.Keyboard('', 'Enter Rapid Access Code')
    kb.doModal()
    if kb.isConfirmed():
        return kb.getText().strip()
    return None

def fetch_api_data(code):
    url = API_URL + code
    headers = {
        'User-Agent': 'Mozilla/5.0',
    }
    try:
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        data = response.read()
        return json.loads(data)
    except Exception as e:
        xbmcgui.Dialog().ok("Error", "Failed to fetch cuteShop API data:\n" + str(e))
        return None

def download(url, output_path):
    progress = xbmcgui.DialogProgress()
    progress.create("Downloading", os.path.basename(output_path))

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': url,
    }

    try:
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)

        total_size = int(response.info().get("Content-Length", 0))
        if total_size <= 0:
            raise Exception("cuteShop API did not report file size.")

        bytes_read = 0
        block_size = 256 * 1024 # Can possibly change this for faster speeds at the expense of stability. Defaults to 256KB block size.
        start_time = time.time()

        with open(output_path, 'wb') as f:
            while True:
                block = response.read(block_size)
                if not block:
                    break
                f.write(block)
                bytes_read += len(block)

                percent = int((bytes_read * 100) / total_size)

                elapsed = time.time() - start_time
                speed = bytes_read / elapsed if elapsed > 0 else 0
                remaining_bytes = total_size - bytes_read
                eta = int(remaining_bytes / speed) if speed > 0 else 0

                mb_downloaded = bytes_read / (1024.0 * 1024.0)
                mb_remaining = remaining_bytes / (1024.0 * 1024.0)
                hours = eta // 3600
                minutes = (eta % 3600) // 60
                seconds = eta % 60

                line1 = output_path
                line2 = "{0:.2f} MB / {1:.2f} MB".format(mb_downloaded, mb_remaining)

                eta_parts = []
                if hours > 0:
                    eta_parts.append("%d hour%s" % (hours, "s" if hours != 1 else ""))
                if minutes > 0:
                    eta_parts.append("%d minute%s" % (minutes, "s" if minutes != 1 else ""))
                if seconds > 0 or not eta_parts:
                    eta_parts.append("%d second%s" % (seconds, "s" if seconds != 1 else ""))
                line3 = ", ".join(eta_parts) + " remaining"


                progress.update(percent, line1, line2, line3)

                if progress.iscanceled():
                    raise Exception("Download canceled.")

        progress.close()
        xbmcgui.Dialog().ok("Success", "Download complete: " + output_path)

    except Exception as e:
        progress.close()
        xbmcgui.Dialog().ok("Error", "Download failed: " + str(e))

def download_boxart(url, output_path):
    progress = xbmcgui.DialogProgress()
    progress.create("Downloading Cover Art...", os.path.basename(output_path))

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': url,
    }

    try:
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)

        total_size = int(response.info().get("Content-Length", 0))
        if total_size <= 0:
            raise Exception("Server did not report file size.")

        bytes_read = 0
        block_size = 256 * 1024
        start_time = time.time()

        with open(output_path, 'wb') as f:
            while True:
                block = response.read(block_size)
                if not block:
                    break
                f.write(block)
                bytes_read += len(block)

                percent = int((bytes_read * 100) / total_size)

                elapsed = time.time() - start_time
                speed = bytes_read / elapsed if elapsed > 0 else 0
                remaining_bytes = total_size - bytes_read
                eta = int(remaining_bytes / speed) if speed > 0 else 0

                mb_downloaded = bytes_read / (1024.0 * 1024.0)
                mb_remaining = remaining_bytes / (1024.0 * 1024.0)
                hours = eta // 3600
                minutes = (eta % 3600) // 60
                seconds = eta % 60

                line1 = output_path
                line2 = "{0:.2f} MB / {1:.2f} MB".format(mb_downloaded, mb_remaining)

                eta_parts = []
                if hours > 0:
                    eta_parts.append("%d hour%s" % (hours, "s" if hours != 1 else ""))
                if minutes > 0:
                    eta_parts.append("%d minute%s" % (minutes, "s" if minutes != 1 else ""))
                if seconds > 0 or not eta_parts:
                    eta_parts.append("%d second%s" % (seconds, "s" if seconds != 1 else ""))
                line3 = ", ".join(eta_parts) + " remaining"


                progress.update(percent, line1, line2, line3)

                if progress.iscanceled():
                    raise Exception("Cover art download canceled.")

        progress.close()

    except Exception as e:
        progress.close()
        xbmcgui.Dialog().ok("Error", "Cover art download failed: " + str(e))

def download_attacher(url, output_path):
    progress = xbmcgui.DialogProgress()
    progress.create("Downloading Attacher...", os.path.basename(output_path))

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': url,
    }

    try:
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)

        total_size = int(response.info().get("Content-Length", 0))
        if total_size <= 0:
            raise Exception("Server did not report file size.")

        bytes_read = 0
        block_size = 256 * 1024
        start_time = time.time()

        with open(output_path, 'wb') as f:
            while True:
                block = response.read(block_size)
                if not block:
                    break
                f.write(block)
                bytes_read += len(block)

                percent = int((bytes_read * 100) / total_size)

                elapsed = time.time() - start_time
                speed = bytes_read / elapsed if elapsed > 0 else 0
                remaining_bytes = total_size - bytes_read
                eta = int(remaining_bytes / speed) if speed > 0 else 0

                mb_downloaded = bytes_read / (1024.0 * 1024.0)
                mb_remaining = remaining_bytes / (1024.0 * 1024.0)
                hours = eta // 3600
                minutes = (eta % 3600) // 60
                seconds = eta % 60

                line1 = output_path
                line2 = "{0:.2f} MB / {1:.2f} MB".format(mb_downloaded, mb_remaining)

                eta_parts = []
                if hours > 0:
                    eta_parts.append("%d hour%s" % (hours, "s" if hours != 1 else ""))
                if minutes > 0:
                    eta_parts.append("%d minute%s" % (minutes, "s" if minutes != 1 else ""))
                if seconds > 0 or not eta_parts:
                    eta_parts.append("%d second%s" % (seconds, "s" if seconds != 1 else ""))
                line3 = ", ".join(eta_parts) + " remaining"


                progress.update(percent, line1, line2, line3)

                if progress.iscanceled():
                    raise Exception("Attacher download canceled.")

        progress.close()

    except Exception as e:
        progress.close()
        xbmcgui.Dialog().ok("cuteShop - Error", "Attacher download failed: " + str(e))

def main():
    code = get_user_code()
    if not code:
        xbmcgui.Dialog().ok("cuteShop - Cancelled", "No Rapid Access Code entered.")
        return

    data = fetch_api_data(code)
    if not data or 'file' not in data:
        xbmcgui.Dialog().ok("cuteShop - Error", "Invalid code or file not found.")
        return

    raw_file_name = data.get('titleID', 'downloaded_file')
    raw_folder_name = data.get('title')
    file_name = sanitize_for_fatx(raw_file_name + ".iso")
    attacher_name = "default.xbe"
    boxart_name = "default.tbn"
    download_url = FILE_URL + code
    attacher_url = ATTACHER_URL.format(data.get('titleID'))
    boxart_url = BOXART_URL.format(data.get('contentID'))

    download_dir = DOWNLOAD_DIRECTORY
    folder_name = sanitize_for_fatx(raw_folder_name)
    game_dir = os.path.join(download_dir, folder_name)

    if not os.path.exists(game_dir):
        os.mkdir(game_dir)

    output_path = os.path.join(game_dir, file_name)
    output_path_attacher = os.path.join(game_dir, attacher_name)
    output_path_cover = os.path.join(game_dir, boxart_name)

    download_attacher(attacher_url, output_path_attacher)
    download_boxart(boxart_url, output_path_cover)
    download(download_url, output_path)

if __name__ == "__main__":
    main()
