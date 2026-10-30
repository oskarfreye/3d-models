// Klemmknauf für das Gelenk der Kamera-/Handyhalterung – PETG, Bambu Lab A1 mini
// Wird ohne Mutter direkt auf die M5-Schraube gedreht: die Schraube schneidet ihr Gewinde selbst.
// Teile: "knauf", "passtest" (Lochgrößen testen)
part = "knauf";

$fn = 96;

// --- Gemessen ---
schraube_d    = 4.77;  // M5, gemessen
scheibe_d     = 15.2;  // Gelenkscheibe, auf die der Knauf drückt
ueberstand    = 2.3;   // Schraube steht so weit über die Scheibe raus (44.65 - 42.34)

// --- Knauf ---
auflage_d     = 14.25; // Druckfläche unten (etwas kleiner als die Scheibe)
griff_d       = 20;    // Griffdurchmesser; 14.25 = bündig mit der Scheibe, aber weniger Kraft
griff_h       = 9;
auflage_h     = 2;     // zylindrischer Hals unter dem Griff
rippen        = 10;    // Griffmulden
mulde_d       = 4;

// --- Gewindeloch (Schraube schneidet selbst) ---
loch_d        = 4.3;   // im Passtest ermitteln: 4.1 = fest, 4.5 = locker
loch_tiefe    = 8;     // reicht auch für eine längere Schraube
fase          = 0.6;   // Einführfase am Loch und an der Unterkante

gesamt_h = auflage_h + griff_h;

module loch() {
    translate([0,0,-0.01]) cylinder(d=loch_d, h=loch_tiefe+0.01);
    // Fase zum Ansetzen der Schraube
    translate([0,0,-0.01]) cylinder(d1=loch_d+2*fase, d2=loch_d, h=fase);
}

module knauf() {
    difference() {
        union() {
            // Hals mit Druckfläche, Unterkante gefast gegen Elefantenfuß
            cylinder(d1=auflage_d-2*fase, d2=auflage_d, h=fase);
            translate([0,0,fase]) cylinder(d=auflage_d, h=auflage_h-fase);
            // Griff mit abgerundeter Oberkante
            translate([0,0,auflage_h]) hull() {
                cylinder(d=griff_d, h=griff_h-1.5);
                cylinder(d=griff_d-3, h=griff_h);
            }
        }
        loch();
        // Griffmulden
        for (i = [0:rippen-1]) rotate(i*360/rippen)
            translate([griff_d/2+mulde_d*0.15, 0, auflage_h-0.01])
                cylinder(d=mulde_d, h=griff_h+0.02, $fn=32);
    }
}

// Platte mit drei Löchern zum Testen, welche Größe sich gut eindrehen lässt und hält
module passtest() {
    tests = [4.1, 4.3, 4.5];
    difference() {
        hull() for (i = [0:2]) translate([i*12,0,0]) cylinder(d=10, h=5);
        for (i = [0:2]) translate([i*12,0,-0.01]) {
            cylinder(d=tests[i], h=5.02);
            cylinder(d1=tests[i]+2*fase, d2=tests[i], h=fase);
        }
        // Markierung: Kerben 1/2/3 = 4.1/4.3/4.5
        for (i = [0:2]) for (k = [0:i]) translate([i*12-2+k*2, -5.5, 4]) cube([0.8, 2, 2]);
    }
}

// Kopfüber gedruckt: flache Oberseite aufs Bett, sonst hängt der Griff über dem Hals in der Luft
if (part == "knauf")    translate([0,0,gesamt_h]) rotate([180,0,0]) knauf();
else if (part == "vorschau") knauf();
else if (part == "passtest") passtest();
