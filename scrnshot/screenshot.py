import subprocess
import tempfile


def do_screenshot(url):
    """
    Screenshot an `url` (fullscreen) and return a path to an image.

    :param url: A previously validated URL of a webpage to capture.
    :return: A Path-like object representing a screenshot.
    """
    _, path = tempfile.mkstemp(suffix='.png')
    cmd = f'firefox -screenshot {path} {url}'.split()
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=10.0)
    return path
