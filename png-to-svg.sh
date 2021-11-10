mkdir -p /tmp/tlhng

for src in lopulliset/*.png; do
    name=$(basename $src .png)
    echo $name
    pnm="/tmp/tlhng/$name.pnm"
    svg="lopulliset/$name.svg"
    convert $src -background white -alpha background $pnm && potrace $pnm -s -o $svg
    #pngtopnm -mix $src > $pnm && potrace $pnm -s -o $svg && rm $pnm
    # set colour
    # sed -i "s/#000000/#016b8f/g" *.svg
    # same for PNG
    # mogrify -fill '#016b8f' -opaque black *.png
done

