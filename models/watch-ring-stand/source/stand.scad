// Watch & ring stand – Bambu Lab A1 mini (180 x 180 x 180 mm)
// One piece, no supports. Raised name on top: change filament at z = base_h.
// Custom name: openscad -D 'name="PAPA"' -o stand.stl stand.scad

name       = "EKKEHARD";
font       = "Avenir Next:style=Demi Bold";
text_size  = 7.5;
text_space = 1.35;   // letter spacing
text_h     = 0.8;    // raised height (4 layers at 0.2 mm)

$fn = 120;

// --- Base ---
base_w   = 170;
base_d   = 85;
base_h   = 11;
base_r   = 14;       // corner radius
chamfer  = 1.6;      // top edge

// --- Watch post (tapered ellipse, a = left/right, b = front/back) ---
post_x     = -42;
post_h     = 80;     // above the base
post_a_bot = 33;  post_b_bot = 18;   // ~164 mm circumference
post_a_top = 26;  post_b_top = 15;   // ~131 mm circumference

// --- Ring tray with two cones ---
tray_x0 = 6;   tray_x1 = 77;
tray_y0 = -22; tray_y1 = 32;
tray_r  = 10;
tray_depth = 6;
cone_xs = [28, 56];
cone_y  = 9;
cone_h  = 52;        // above the tray floor
cone_d_bot = 23;     // fits ring sizes up to ~23 mm inner diameter
cone_d_top = 11;

// --- Felt pad pockets on the bottom ---
pad_d = 10.5;  pad_depth = 1;

module rrect(w, d, r) offset(r) square([w - 2*r, d - 2*r], center = true);

module base() {
    hull() {
        linear_extrude(base_h - chamfer) rrect(base_w, base_d, base_r);
        linear_extrude(base_h) rrect(base_w - 2*chamfer, base_d - 2*chamfer, base_r - chamfer);
    }
}

module tray2d()
    translate([(tray_x0 + tray_x1)/2, (tray_y0 + tray_y1)/2])
        rrect(tray_x1 - tray_x0, tray_y1 - tray_y0, tray_r);

module tray_cut() {
    // rounded floor edge: hull of an inset outline at the floor and the full outline above
    hull() {
        translate([0, 0, base_h - tray_depth]) linear_extrude(0.01) offset(-3) tray2d();
        translate([0, 0, base_h - tray_depth + 3]) linear_extrude(tray_depth) tray2d();
    }
}

module post()
    translate([post_x, 0, base_h - 0.01])
        hull() {
            scale([post_a_bot, post_b_bot, 1]) cylinder(r = 1, h = 0.01);
            translate([0, 0, post_h - post_b_top * 0.8])
                scale([post_a_top, post_b_top, post_b_top * 0.8]) sphere(r = 1);
        }

module cone(x)
    translate([x, cone_y, base_h - tray_depth - 0.01])
        hull() {
            cylinder(d = cone_d_bot, h = 0.01);
            translate([0, 0, cone_h - cone_d_top/2]) sphere(d = cone_d_top);
        }

module name_text()
    translate([0, -base_d/2 + 9, base_h - 0.01])
        linear_extrude(text_h + 0.01)
            text(name, size = text_size, font = font, spacing = text_space,
                 halign = "center", valign = "center");

module pads()
    for (x = [-base_w/2 + 16, base_w/2 - 16], y = [-base_d/2 + 14, base_d/2 - 14])
        translate([x, y, -1]) cylinder(d = pad_d, h = pad_depth + 1);

module stand() {
    difference() {
        union() { base(); post(); }
        tray_cut();
        pads();
    }
    for (x = cone_xs) cone(x);
    name_text();
}

stand();
