mkdir -p /tmp/tlhng

for src in tavumerkit/*.svg; do
    name=$(basename $src .svg)
    echo $name
    png="/tmp/tlhng/$name.png"
    pnm="/tmp/tlhng/$name.pnm"
    svg="lopulliset/$name.svg"
    rsvg-convert $src -o $png
    convert $png -background white -alpha background $pnm && potrace $pnm -s -o $svg
    #pngtopnm -mix $src > $pnm && potrace $pnm -s -o $svg && rm $pnm
    # set colour
    # sed -i "s/#000000/#016b8f/g" *.svg
    # same for PNG
    # mogrify -fill '#016b8f' -opaque black *.png
done

