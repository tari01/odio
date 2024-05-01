# 24.5.1

 - Translated using Weblate (Portuguese (Brazil)) (863e079)

# 23.12.1

 - odio/gst.py: Fix file name escaping (da28466)
 - Translated using Weblate (Turkish) (d9d8d77)
 - Translated using Weblate (Spanish) (bc91f1c)

# 23.11.1

 - odio/tagdialog.py: Lowercase 'N (133bc3a)
 - odio/tagdialog.py: Use requests-html for AllMusic page parsing (5328345)

# 23.10.1

 - Translated using Weblate (Russian) (5f13f70)
 - Translated using Weblate (Russian) (5f3c345)
 - Translated using Weblate (Russian) (2bf65ad)
 - odio/gst.py: Escape backslashes in file names (912d58b)

# 23.8.1

 - odio/gst.py: Report if the GstTag.TagImageType.FRONT_COVER bug is fixed (e2329f1)
 - data/usr/bin/odio: Add colour scheme handler (d6f300b)

# 23.7.1

 - odio/gst.py: Fix wrong tag image type (c08f4d1)
 - data/usr/bin/odio: Catch and report invalid SACD error (22d672b)

# 23.6.1

 - odio/titlecase.py: Lowercase 'du' (69a4240)
 - Translated using Weblate (English (United Kingdom)) (cb52bcc)
 - Catch decoding errors and show dialog (1da478e)

# 23.4.1

 - data/usr/bin/odio: Fix progress bar freeze during keyboard seek (90c92b9)
 - data/usr/bin/odio: Use emblemed icon for Delete Images button (eeb7afe)
 - odio/titlecase.py: Lowercase 'as' (3e71dc8)
 - odio/tagdialog.py: Lovercase 'reprise' (0657527)
 - Add track length column (4a571f1)
 - odio/gst.py: Discard existing tags (eb342c2)
 - odio/gst.py: Save track replay gain as extended comment (ea3fc6a)

# 23.1.31

 - Translated using Weblate (Spanish) (eaf3636)

# 22.10.31

 - Translated using Weblate (Norwegian Bokmål) (5f5a45e)
 - Translated using Weblate (Turkish) (1e22f65)
 - odio/tagdialog.py: Only save image path if there were no load errors (715cb31)
 - po/*: Update translation files (542ad52)
 - odio/tagdialog.py: Catch wrong image format (45e207a)
 - odio/gst.py: Drop control characters from malformed cuesheets (3e44607)
 - odio/gst.py: Also search for *.wv files when looking for cuesheet sources (41eddb6)
 - data/usr/bin/odio: Fix ignoring duplicate cuesheets pointing to the same source file (336770f)
 - data/usr/bin/odio: Add seek jump via arrow keys (4430a50)
 - Translated using Weblate (Turkish) (06cb255)

# 22.7.5

 - Remove defaults for the genre and comment tags (772f413)
 - data/usr/bin/odio: Make sure we seek within playing track boundaries (778e98e)
 - data/usr/bin/odio: Fix successive seeks blocking playback (1fc42ba)
 - data/usr/bin/odio: Update TreeSelection whenever an encoded file is removed (a147e6b)
 - Updated translation files (b3fa8a7)
 - odio/gst.py: Ignore cuefiles with multiple FILE lines (ebf3838)
 - Add checkbox to tagdialog base folder combo (e7a7550)
 - odio/gst.py: Do not log APE decoding errors (6125cc4)
 - Ignore duplicate cuesheets pointing to the same source file (18eef34)
 - odio/gst.py: If the cuesheet's FILE does not exist, search for any single audio file in the same folder (8dd2bf2)
 - data/usr/bin/odio: Start GstSplitter only if no other tasks are running (853cd70)
 - odio/tagdialog.py: Autoformat ’ to ' (d3654e3)
 - odio/tagdialog.py: Replace double dash (a1715c2)
 - odio/sacd.py: Fix SACD ISO track numbering (cc98ecc)
 - odio/titlecase.py: Lowercase 'di' (a2e7bbc)
 - Translated using Weblate (Portuguese (Brazil)) (c4eb05a)
 - Translated using Weblate (Spanish) (bda8a96)
 - odio/gst.py: Provide some defaults for the genre and comment tags (228655a)
 - data/usr/bin/odio: Use a default base path (d162b12)
 - odio/titlecase.py: Lowercase 'des' (6f6b780)

# 22.5.15

 - odio/titlecase.py: Lowercase 'without' (e47bc32)
 - odio/tagdialog.py: Add some more auto formatting rules (aaf7e7d)
 - debian/postinst: Drop file (2260153)
 - odio/tagdialog.py: Add some more title autoformating rules (2169ba9)
 - po/odio.pot: Update translation catalogue (7ade1c3)
 - odio/tagdialog.py: Collapse multiple spaces when autoformatting (d7ebe4b)
 - po/odio.pot: Update translation catalogue (f0357c4)
 - Add multiple base paths (b853f2b)
 - data/usr/bin/odio: Add SIGINT handler (2bd0b2d)
 - Fix DSF/DFF track numbers and list order (fc2f073)
 - odio/sacd.py: Make all class variables private to instance (6079c63)
  - odio/tagdialog.py: Lowercase 'Remix' in titles (29291dc)
 - Ignore cuesheets with multiple FILE sections (bbb13c9)
 - odio/gst.py: Fall back to FLAC cuesheet source if WAV/APE are not found (3f9def3)
 - odio/gst.py: Change cuesheet decoding fallback order (1106708)
 - po/odio.pot: Update translation catalog (6f07a8d)
 - Catch and warn about cuesheets with a bad FILE line (8c4b2a8)
 - data/usr/bin/odio: Wait for all tasks to finish before starting analysis (456a853)
 - odio/gst.py: Open cuesheet as binary and try multiple decoders (8679e39)
 - odio/gst.py: Try to parse APE with cuesheet if WAV does not exist (ca428dc)

# 22.5.8

 - odio/gst.py: Switch to GstAudio.AudioInfo.new_from_caps (3f1c2c1)
 - Translated using Weblate (Russian) (30ae70d)
 - Translated using Weblate (Chinese (Simplified)) (86188fc)
 - Translated using Weblate (Chinese (Simplified)) (4ce10ca)

# 21.11.13

 - Translated using Weblate (Turkish) (0db0d77)
 - Update translation file (851153c)
 - Move SACD decoding to separate module (05bbeb0)
 - odio/streamsdialog.py: Do not display chapters shorter than 1 second (2f2c392)
 - odio/streamsdialog.py: Escape single quotes in lsdvd output (d6deb7a)
 - Translated using Weblate (Spanish) (5400da6)

# 21.4.30

 - Translated using Weblate (Chinese (Simplified)) (f782ada)
 - Translated using Weblate (English (United Kingdom)) (931e4e1)
 - odio/gst.py: Add native dsf/dff decoding (7791100)
 - Translated using Weblate (Russian) (6da4de8)
 - data/usr/bin/odio: Send files to Odio Edit in natural order (a3a19f6)

# 21.3.28

 - odio/titlecase.py: Add 'del' to lowercase list (314938a)
 - odio/streamsdialog.py: Fix selected title index (2c1b9b9)
 - Translated using Weblate (Turkish) (ae66383)
 - po: update translation files (69913e8)
 - odio/titlecase.py: lowercase 'over' (8c16bad)
 - Translated using Weblate (Sinhala) (d06ad36)

# 21.2.28

 - Add setting to disable automatic title-casing (08aa1d6)
 - Added translation using Weblate (Sinhala) (c5674a8)
 - Decode 64 and 32-bit audio to their actual used bits (85abcb0)
 - Translated using Weblate (Portuguese (Brazil)) (af96bc8)
 - Decode floating-point audio as S32LE (a5a515e)
 - Added *.mka to supported files (26c3d08)
 - Minor channel manipulation tweaks (54ccd1e)

# 21.2.13

 - Always saturate 6.1 input to 7.1 (9b19359)
 - Set WAVE header AudioFormat to \x01\x00 for quad, 5.0 and 7.1 input (d81c715)

# 21.2.10

 - Fix 8-channel Flac encoding (ec14d57)
 - Drop second param from reorderChannels (725613f)
 - Fix typo (85cb25c)

# 21.1.31

 - Fix APPDEBUG import (dbf2caf)
 - Translated using Weblate (Turkish) (037d260)
 - Fix window positioning (266c891)
 - Insert desktop file translations during setup (49be6e7)
 - Fix function name (f801011)

# 21.1.9

 - Trim spaces from pasted text in tag dialog (33fc3dd)
 - Some translation tweaks (fca5bc7)
 - Translated using Weblate (Norwegian Bokmål) (e5e960a)
 - Added translation using Weblate (Norwegian Bokmål) (d38e0f3)
 - Translated using Weblate (French) (1c8efa2)
 - Translated using Weblate (English (United Kingdom)) (09fbaf7)
 - Remove duplicated translation (484fc3f)
 - Remove untranslated languages (624fe65)
 - Update translation file (ad6f755)
 - Replace weird characters in cue sheet parser (f21a823)
 - Rename some variables (85a2104)
 - Do not read DVDs with no LPCM audio (0c8498b)
 - Drop unneded dependencies (0106041)
 - Some code refactoring (24132d0)
 - Improve AAC progress display (96d8a45)
 - Improve AAC progress display (15ef121)
 - Scroll to bottom when a new file is added (f3c37e9)
 - Use format function instead of % (f40ab26)
 - Read supported extensions from Gtk.FileFilterInput (73230c9)
 - Delete temp files (7ee4326)
 - gst.py: Use a function to escape file paths (b2a10b2)
 - Show silence column in debug mode only (4115fee)
 - Make output paths EXT4/FAT32 friendly (39de8d2)
 - Fix progress text ticker in status bar (dd15990)
 - Fix file analysis after editing (6cec040)
 - Use 'Ready' for all completed operations (7c3b0d7)
 - Remove deprecated GLib.USER_DIRECTORY_* enums (6523ec1)
 - Show progress text when encoding starts (4c0cd8e)
 - Update progress directly, not via GLib.idle (52add32)
 - Migrate from Launchpad (97a2b21)
