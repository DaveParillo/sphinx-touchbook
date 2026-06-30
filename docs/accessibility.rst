.. Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
   Copyright (C) 2026 Dave Parillo.
   See https://daveparillo.github.io/sphinx-touchbook/ for details.

Accessibility And Keyboard Use
==============================

Touchbook directives use native HTML controls wherever possible. Buttons,
inputs, text areas, selects, links, and dialogs keep their browser keyboard
behavior and programmatic labels. This helps assistive technology and lets each
browser expose controls in the way users expect.

Keyboard Basics
---------------

Most Touchbook controls follow standard browser behavior:

* ``Tab`` moves forward through focusable controls.
* ``Shift+Tab`` moves backward through focusable controls.
* ``Enter`` activates links and most buttons.
* ``Space`` activates buttons, checkboxes, radio buttons, and similar controls.
* Arrow keys may move within composite widgets, such as tab groups.

Tab Groups
----------

The ``tb-group`` directive renders an ARIA tab interface. Only the selected tab
is in the normal ``Tab`` order. This is intentional and follows the common
roving-tabindex pattern for tabs.

When focus is on a tab:

* ``ArrowRight`` moves to the next tab.
* ``ArrowLeft`` moves to the previous tab.
* ``Home`` moves to the first tab.
* ``End`` moves to the last tab.
* ``Tab`` moves into the selected tab panel when that panel contains a
  focusable control.

For example, if a ``tb-group`` has ``Source`` and ``Rendered`` tabs, ``Tab``
does not normally move from ``Source`` to ``Rendered``. Use the arrow keys to
select ``Rendered``. Then use ``Tab`` to enter the rendered content.

Platform Settings
-----------------

Keyboard navigation can depend on operating system and browser settings. If
``Tab`` skips buttons or other native controls, check the platform settings
before assuming the page is broken.

macOS
   In System Settings, open **Keyboard** and enable full keyboard navigation.
   Safari also has a browser-specific setting in **Advanced** named
   **Press Tab to highlight each item on a webpage**.

   When full keyboard access is disabled, macOS browsers may require
   ``Option+Tab`` or ``Alt+Tab`` to move to buttons and other controls.

Windows
   Windows browsers usually include buttons in the normal ``Tab`` order. If
   navigation seems incomplete, check browser accessibility settings and any
   installed keyboard or assistive-technology utilities. In Microsoft Edge and
   Chrome, also check whether caret browsing or extension settings are changing
   keyboard behavior.

Linux
   Linux behavior depends on the desktop environment, browser, and assistive
   technology stack. GNOME, KDE, Firefox, Chrome, and Chromium usually include
   native buttons in the normal ``Tab`` order. If they do not, check desktop
   keyboard accessibility settings, browser settings, and screen-reader or
   extension configuration.

Testing Guidance
----------------

When testing Touchbook content for keyboard accessibility:

* Test with full keyboard navigation enabled.
* Confirm that every visible control can receive focus.
* Confirm that visible focus is easy to see.
* Activate buttons with ``Space`` and ``Enter``.
* Test ``tb-group`` tabs with arrow keys, not only with ``Tab``.
* Test the static fallback output when building text or PDF formats.

Touchbook should provide accessible controls and predictable focus behavior.
Operating system and browser settings can still change how users move through
native controls.
