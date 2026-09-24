import struct
import zlib
from pathlib import Path

# A deterministic one-pixel fixture, expanded at build time.
def chunk(kind, data):
    return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))

Path(__file__).with_name('pixel.png').write_bytes(
    b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', 1, 1, 8, 2, 0, 0, 0)) +
    chunk(b'IDAT', zlib.compress(b'\0\0\0\xff')) + chunk(b'IEND', b''))

Path(__file__).with_name('long-table.rst').write_text(
    '.. list-table:: A multi-page table\n   :header-rows: 1\n   :class: longtable\n\n'
    '   * - Item\n     - Description\n' + ''.join(
        f'   * - {i}\n     - Repeated table body row {i}.\n' for i in range(80)))

extensions = ['sphinx_touchbook']
project = 'Touchbook PDF accessibility fixture'
author = 'Touchbook'
tb_pdf_tagging = True
tb_pdf_language = 'en-US'
latex_use_xindy = False
latex_documents = [('index', 'fixture.tex', project, author, 'manual')]
