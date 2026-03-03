# PKGBUILD
# Maintainer: Your Name <jknierum@gmail.com>

pkgname=ttoad
pkgver=1.0.0
pkgrel=1
pkgdesc="Ttoad: a Tiny terminal model code editor"
arch=('any')
url="https://github.com/jknierum/ttoad"
license=('MIT')
depends=('python' 'wl-clipboard')
makedepends=('python-setuptools')
optdepends=('xclip: for X11 clipboard support')
source=("$pkgname-$pkgver.tar.gz::https://github.com/jknierum/$pkgname/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname-$pkgver"

    # Create necessary directories
    install -dm755 "$pkgdir/usr/bin"
    install -dm755 "$pkgdir/usr/lib/python3.10/site-packages/syntax"
    install -dm755 "$pkgdir/usr/share/doc/$pkgname"
    install -dm755 "$pkgdir/usr/share/applications"
    install -dm755 "$pkgdir/usr/share/licenses/$pkgname"

    # Install the main editor script
    install -Dm755 ttoad.py "$pkgdir/usr/bin/ttoad"

    # Install syntax highlighting module
    cp -r syntax/* "$pkgdir/usr/lib/python3.10/site-packages/syntax/"

    # Install documentation
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE" 2>/dev/null || true

    # Create a simple man page (optional)
    install -dm755 "$pkgdir/usr/share/man/man1"
    cat > "$pkgdir/usr/share/man/man1/ttoad.1" << EOF
.TH TTOAD 1 "March 2026" "ttoad 1.0.0" "User Commands"
.SH NAME
ttoad \- Tiny terminal model code editor
.SH SYNOPSIS
.B ttoad
[\fIFILE\fR]
.SH DESCRIPTION
Ttoad is a tiny terminal-based code editor with syntax highlighting.
.SH OPTIONS
.TP
\fIFILE\fR
File to edit (creates new file if it doesn't exist)
.SH KEYBINDINGS
.TP
Ctrl+S
Save file
.TP
Ctrl+Q
Quit editor
.TP
Ctrl+Space
Toggle select mode
.SH AUTHOR
Written by Your Name.
EOF

    # Install desktop entry
    cat > "$pkgdir/usr/share/applications/ttoad.desktop" << EOF
[Desktop Entry]
Name=Ttoad
GenericName=Text Editor
Comment=Tiny terminal model code editor
Exec=ttoad %F
Icon=accessories-text-editor
Terminal=true
Type=Application
Categories=Development;TextEditor;
Keywords=editor;text;code;python;
StartupNotify=false
MimeType=text/plain;
EOF

    # Create a simple icon (optional - you can use a default terminal icon)
    install -dm755 "$pkgdir/usr/share/icons/hicolor/48x48/apps"
    # If you have an icon, copy it here
    # install -Dm644 icon.png "$pkgdir/usr/share/icons/hicolor/48x48/apps/ttoad.png"
}

# Optional: Add post-installation message
post_install() {
    echo ":: Ttoad has been installed successfully!"
    echo ":: Run 'ttoad' to start editing"
    echo ":: For help, check the man page: man ttoad"
}
