# PKGBUILD - Complete working version
pkgname=ttoad-git
pkgver=1.0.0.r0.gddb5a08
pkgrel=5
pkgdesc="Ttoad: a Tiny terminal model code editor"
arch=('any')
url="https://github.com/jknierum/ttoad"
license=('MIT')
depends=('python' 'wl-clipboard')
makedepends=('git')
source=("git+https://github.com/jknierum/ttoad.git")
sha256sums=('SKIP')

package() {
  cd "$srcdir/ttoad"

  # Python version
  python_version=3.14
  site_packages="/usr/lib/python$python_version/site-packages"

  # Create module directory structure
  mkdir -p "$pkgdir$site_packages/ttoad/syntax"

  # Install main module as __main__.py
  install -Dm644 ttoad.py "$pkgdir$site_packages/ttoad/__main__.py"

  # Create __init__.py
  cat > "$pkgdir$site_packages/ttoad/__init__.py" << 'EOF'
"""Ttoad editor package"""
import sys
from .__main__ import main

def main():
    return main()

if __name__ == '__main__':
    sys.exit(main())
EOF

  # Install syntax module
  if [ -d "syntax" ]; then
    for file in syntax/*.py; do
      if [ -f "$file" ]; then
        install -Dm644 "$file" "$pkgdir$site_packages/ttoad/syntax/$(basename $file)"
      fi
    done
    # Ensure __init__.py exists in syntax
    touch "$pkgdir$site_packages/ttoad/syntax/__init__.py"
  fi

  # Create a proper console script (not using entry points)
  mkdir -p "$pkgdir/usr/bin"
  cat > "$pkgdir/usr/bin/ttoad" << 'EOF'
#!/bin/bash
exec python3 -m ttoad "$@"
EOF
  chmod 755 "$pkgdir/usr/bin/ttoad"

  # Create egg-info for pacman (so it knows the package is installed)
  mkdir -p "$pkgdir$site_packages/ttoad-1.0.0-py$python_version.egg-info"

  cat > "$pkgdir$site_packages/ttoad-1.0.0-py$python_version.egg-info/PKG-INFO" << EOF
Metadata-Version: 2.1
Name: ttoad
Version: 1.0.0
Summary: Tiny terminal model code editor
Home-page: https://github.com/jknierum/ttoad
License: MIT
EOF

  echo "ttoad" > "$pkgdir$site_packages/ttoad-1.0.0-py$python_version.egg-info/top_level.txt"
  touch "$pkgdir$site_packages/ttoad-1.0.0-py$python_version.egg-info/dependency_links.txt"

  # Create entry_points.txt that won't interfere
  cat > "$pkgdir$site_packages/ttoad-1.0.0-py$python_version.egg-info/entry_points.txt" << EOF
[console_scripts]
ttoad = ttoad:main
EOF

  # Verify installation
  echo "=== Files installed to $pkgdir$site_packages/ttoad/ ==="
  find "$pkgdir$site_packages/ttoad" -type f -name "*.py" | sort
}

post_install() {
  echo ""
  echo "╔════════════════════════════════════╗"
  echo "║     Ttoad installed successfully!  ║"
  echo "╚════════════════════════════════════╝"
  echo "Run 'ttoad' to start editing"
  echo "For help: ttoad --help"
}
