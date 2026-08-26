#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:-0.1.0}"
ARCH="${ARCH:-amd64}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_ROOT="$ROOT/build/deb"
PACKAGE_ROOT="$BUILD_ROOT/demineur_${VERSION}_${ARCH}"
OUTPUT="$ROOT/dist/demineur_${VERSION}_${ARCH}.deb"

cd "$ROOT"

if ! python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
    echo "Erreur : Python 3.10 ou une version plus récente est requis." >&2
    echo "Recréez .venv avec : python3.10 -m venv .venv" >&2
    exit 1
fi

if ! python3 -c 'import PyInstaller' 2>/dev/null; then
    echo "Erreur : PyInstaller est absent de l'environnement Python actif." >&2
    echo "Installez les dépendances avec : python -m pip install -r requirements-desktop.txt" >&2
    exit 1
fi

rm -rf "$BUILD_ROOT" "$ROOT/build/demineur" "$ROOT/dist/demineur"
mkdir -p "$ROOT/dist"

python3 -m PyInstaller --clean --noconfirm demineur.spec

mkdir -p \
    "$PACKAGE_ROOT/DEBIAN" \
    "$PACKAGE_ROOT/usr/bin" \
    "$PACKAGE_ROOT/usr/share/applications" \
    "$PACKAGE_ROOT/usr/share/icons/hicolor/scalable/apps" \
    "$PACKAGE_ROOT/usr/share/doc/demineur"

install -m 0755 "$ROOT/dist/demineur" "$PACKAGE_ROOT/usr/bin/demineur"
install -m 0644 "$ROOT/packaging/demineur.desktop" "$PACKAGE_ROOT/usr/share/applications/demineur.desktop"
install -m 0644 "$ROOT/static/demineur.svg" "$PACKAGE_ROOT/usr/share/icons/hicolor/scalable/apps/demineur.svg"
install -m 0644 "$ROOT/README.md" "$PACKAGE_ROOT/usr/share/doc/demineur/README.md"

cat > "$PACKAGE_ROOT/DEBIAN/control" <<EOF
Package: demineur
Version: $VERSION
Section: games
Priority: optional
Architecture: $ARCH
Maintainer: Guillaume Boileau <guillaume.boileaupro@gmail.com>
Depends: libc6 (>= 2.31), libgl1, libegl1, libxkbcommon-x11-0, libxcb-cursor0
Description: Démineur desktop pour Ubuntu
 Jeu de strategie local pour deux joueurs avec chronometre, score,
 statistiques et historique persistant.
EOF

dpkg-deb --build --root-owner-group "$PACKAGE_ROOT" "$OUTPUT"
echo "$OUTPUT"
