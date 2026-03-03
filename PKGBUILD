# PKGBUILD
# Maintainer: Your Name <jknierum@gmail.com>

pkgname=ttoad-git  # Note the -git suffix for VCS packages
pkgver=1.0.0
pkgrel=1
pkgdesc="Ttoad: a Tiny terminal model code editor (git version)"
arch=('any')
url="https://github.com/jknierum/ttoad"
license=('MIT')
depends=('python' 'wl-clipboard')
makedepends=('git')
# Git source
source=("git+https://github.com/jknierum/ttoad.git")
sha256sums=('SKIP')  # Git sources don't have checksums

pkgver() {
  cd "$srcdir/ttoad"
  git describe --long --tags | sed 's/^v//;s/\([^-]*-g\)/r\1/;s/-/./g'
}

package() {
  cd "$srcdir/ttoad"

  # Get Python version
  python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

  # Install main script
  install -Dm755 ttoad.py "$pkgdir/usr/bin/ttoad"

  # Install syntax module
  install -dm755 "$pkgdir/usr/lib/python$python_version/site-packages/syntax"
  install -Dm644 syntax/__init__.py "$pkgdir/usr/lib/python$python_version/site-packages/syntax/__init__.py"
  install -Dm644 syntax/engine.py "$pkgdir/usr/lib/python$python_version/site-packages/syntax/engine.py"

  # Install docs if they exist
  [ -f README.md ] && install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
}
