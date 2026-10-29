// Twist-Lampe für LED-Puck – Bambu Lab A1 mini (180 x 180 x 180 mm)
// Teile: "sockel" (schwarz), "schirm" (weiß, Vasenmodus), "schriftzug" (gelb), "alles" (Vorschau)
part = "alles";

$fn = 180;

// --- LED-Puck MH001 (gemessen) ---
puck_d     = 59.55;
puck_h     = 9;      // ANNAHME – bitte nachmessen und anpassen
puck_spiel = 0.75;   // Luft im Durchmesser
kabel_b    = 5;      // Breite Kabelkanal
loch_d     = 44;     // Loch unter dem Puck für Stecker + Schalter

// --- Sockel ---
sockel_r     = 50;
sockel_h     = 22;
front_y      = -43;  // abgeflachte Front für den Schriftzug
kragen_h     = 6;    // Ring, über den der Schirm gesteckt wird
kragen_r     = 43.3;

// --- Schirm ---
schirm_h      = 150;
schirm_r_unten = 44;   // passt über den Kragen (Wand im Vasenmodus ~0,6 mm)
gerade_h      = 12;    // runder Steckbereich unten
rippen        = 24;
rippen_tiefe  = 3;
drehung       = 90;    // Grad über die ganze Höhe
seg_theta     = 360;
seg_z         = 150;

// --- Schriftzug ---
name        = "HELLO";  // eigener Text: openscad -D 'name="DEIN NAME"'
schrift     = "Futura:style=Bold";
schrift_gr  = 11;
tasche_tief = 1.0;
buchst_dick = 1.6;     // steht 0,6 mm vor
buchst_luft = 0.12;

pocket_r = (puck_d + puck_spiel) / 2;
gesamt_h = sockel_h + kragen_h;

module name2d(luft = 0)
    offset(delta = -luft)
        text(name, size = schrift_gr, font = schrift, halign = "center", valign = "center");

module sockel() {
    difference() {
        union() {
            // Körper mit Fasen und abgeflachter Front
            intersection() {
                rotate_extrude()
                    polygon([[0,0],[sockel_r-0.8,0],[sockel_r,0.8],
                             [sockel_r,sockel_h-1.5],[sockel_r-1.5,sockel_h],[0,sockel_h]]);
                translate([-sockel_r, front_y, 0]) cube([2*sockel_r, 2*sockel_r, sockel_h]);
            }
            // Kragen für den Schirm
            translate([0,0,sockel_h-0.01])
                cylinder(r1 = kragen_r, r2 = kragen_r - 0.6, h = kragen_h);
        }
        // Tasche für den Puck (Oberseite 0,5 mm unter Kragenkante)
        translate([0,0,gesamt_h - puck_h - 0.5]) cylinder(r = pocket_r, h = puck_h + 1);
        // Großes Loch unter dem Puck: Stecker und Schalter passen durch,
        // Puck liegt auf dem Rand auf und lässt sich von unten herausdrücken
        translate([0,0,-1]) cylinder(d = loch_d, h = gesamt_h);
        // Kabel: Schlitz vom Loch zur Puck-Kante (Schlüsselloch), dann Kanal unten nach hinten raus
        translate([-kabel_b/2, loch_d/2 - 2, -1]) cube([kabel_b, pocket_r - loch_d/2 + 6, gesamt_h + 2]);
        translate([-kabel_b/2, 0, -1]) cube([kabel_b, sockel_r + 1, 6]);
        // Tasche für den Schriftzug in der Front
        translate([0, front_y + tasche_tief, sockel_h/2])
            rotate([90,0,0])
                linear_extrude(tasche_tief + 1) name2d();
    }
}

module schriftzug() linear_extrude(buchst_dick) name2d(buchst_luft);

// Profilradius ohne Rippen
function radius(z) =
    let(t = max(0, z - gerade_h) / (schirm_h - gerade_h))
    schirm_r_unten + 40*t*(1-t)*(1-0.3*t) - 8*t*t;
function smooth(x) = let(c = min(1, max(0, x))) c*c*(3-2*c);
function rippe(z) = rippen_tiefe * smooth((z - gerade_h) / 12);

module schirm() {
    pts = [for (j = [0:seg_z]) let(z = schirm_h * j / seg_z, tw = drehung * z / schirm_h)
              for (i = [0:seg_theta-1]) let(a = 360 * i / seg_theta,
                  r = radius(z) + rippe(z) * (cos(rippen * (a - tw)) - 1) / 2)
                  [r*cos(a), r*sin(a), z]];
    n = seg_theta;
    seiten = [for (j = [0:seg_z-1]) for (i = [0:n-1])
                 let(a = j*n + i, b = j*n + (i+1)%n)
                 [a, b, b+n, a+n]];
    boden = [[for (i = [n-1:-1:0]) i]];
    deckel = [[for (i = [0:n-1]) seg_z*n + i]];
    polyhedron(pts, concat(boden, seiten, deckel));
}

if (part == "sockel") sockel();
else if (part == "schirm") schirm();
else if (part == "schriftzug") schriftzug();
else if (part == "alles") {
    color("#222") sockel();
    color("white", 0.9) translate([0,0,sockel_h]) schirm();
    color("gold") translate([0, front_y + tasche_tief, sockel_h/2])
        rotate([90,0,0]) schriftzug();
}
