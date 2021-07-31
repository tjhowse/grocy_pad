pad_corner_r = 10;
pad_x = 53.85;
pad_y = 107.85;
pad_z = 17.42;
pad_pins_offset_y = 6.5;

module rounded_box(size_x, size_y, size_z, radius) {
    hull() {
        translate([size_x-radius, size_y-radius, 0]) cylinder(r=radius, h=size_z);
        translate([size_x-radius, -size_y+radius, 0]) cylinder(r=radius, h=size_z);
        translate([-size_x+radius, size_y-radius, 0]) cylinder(r=radius, h=size_z);
        translate([-size_x+radius, -size_y+radius, 0]) cylinder(r=radius, h=size_z);
    }
}

module pad() {
    rounded_box(pad_x, pad_y, pad_z, pad_corner_r);
}

dock_back_z = 10;
dock_extra_bottom_lip_y = 5;

dock_x = pad_x;
dock_y = pad_y+dock_extra_bottom_lip_y;
dock_z = pad_z + dock_back_z;

// TODO add a cutout to house the pogo pin contacts once I settle on a part number.
module dock() {
    difference() {
        rounded_box(dock_x, dock_y, dock_z, pad_corner_r);
        translate([0,dock_extra_bottom_lip_y, dock_back_z]) pad();
    }
}

dock();