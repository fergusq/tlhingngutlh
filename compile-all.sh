echo "Siivotaan..."

mkdir -p soluautomaatti/generoidut
mkdir -p lopulliset

rm soluautomaatti/generoidut/*
rm lopulliset/*

echo "Luodaan automaattiset merkit..."

(cd soluautomaatti && python3 tee.py)
cp soluautomaatti/generoidut/* lopulliset/

echo "Muutetaan automaattiset merkit SVG:ksi..."
./png-to-svg.sh | tqdm --total=$(ls lopulliset | wc -l) >/dev/null

echo "Puhdistetaan manuaaliset merkit..."
./copy-custom.sh | tqdm --total=$(ls tavumerkit | wc -l) >/dev/null

echo "Luodaan fontit..."
./create-font.sh

echo "Valmis!"
