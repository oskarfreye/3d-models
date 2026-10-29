// Passtest: oberer Teil vom Sockel (Puck + Steckring) und unterer Rand vom Schirm
include <lampe.scad>
part = "keins";
teil = "sockelring";
if (teil == "sockelring")
    // obere 10 mm vom Sockel, umgedreht nicht nötig: unten abschneiden und flach legen
    translate([0,0,-(gesamt_h-10)]) intersection() {
        sockel();
        translate([-100,-100,gesamt_h-10]) cube([200,200,20]);
    }
else
    intersection() { schirm(); cylinder(r=60, h=15); }
