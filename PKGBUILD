# PKGBUILD - Fixed version
pkgname=ttoad-git
pkgver=1.0.0.r0.gddb5a08
pkgrel=4
pkgdesc="Ttoad: a Tiny terminal model code editor"
arch=('any')
url="https://github.com/jknierum/ttoad"
license=('MIT')
depends=('python' 'wl-clipboard')
makedepends=('git' 'python-setuptools')
source=("git+https://github.com/jknierum/ttoad.git")
sha256sums=('SKIP')

prepare() {
  cd "$srcdir/ttoad"

  # Create proper Python package structure
  mkdir -p ttoad

  # Move main file to __main__.py
  cp ttoad.py ttoad/__main__.py

  # Create __init__.py
  cat > ttoad/__init__.py << 'EOF'
"""Ttoad editor package"""
import sys
from .__main__ import main

if __name__ == "__main__":
    sys.exit(main())
EOF

  # Copy syntax module into the package
  if [ -d "syntax" ]; then
    cp -r syntax ttoad/
    # Ensure __init__.py exists in syntax
    touch ttoad/syntax/__init__.py
  fi

  # Create setup.py
  cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="ttoad",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "ttoad = ttoad:main",
        ],
    },
)
EOF
}

package() {
  cd "$srcdir/ttoad"

  # Install using setuptools
  python setup.py install --root="$pkgdir" --optimize=1 --skip-build

  # Verify the module was installed
  echo "=== Installed files ==="
  find "$pkgdir" -type f -name "*.py" | sort
}

post_install() {
  echo "Ttoad has been installed successfully!"
  echo "Run 'ttoad' to start editing"
}
