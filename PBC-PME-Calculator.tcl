#
# Author: Dr. Rohan J Meshram
# Bioinformatics Centre, Savitribai Phule Pune University
# Email- rohan@bioinfo.net.in or rohan.meshram@unipune.ac.in


# Select all atoms
set everyone [atomselect top all]

# Measure min and max values
set minmax [measure minmax $everyone]
set center [measure center $everyone]

# Extract min and max coordinates
set min [lindex $minmax 0]
set max [lindex $minmax 1]

# Calculate the cell basis vectors
set x_basis [expr {[lindex $max 0] - [lindex $min 0]}]
set y_basis [expr {[lindex $max 1] - [lindex $min 1]}]
set z_basis [expr {[lindex $max 2] - [lindex $min 2]}]

# Function to round the PME grid size to the nearest multiple of 2, 3, or 5
proc roundTo235 {value} {
    # Get the nearest number that is a multiple of 2, 3, or 5
    set factors [list 2 3 5]
    set min_diff 1000000
    set rounded_value $value
    
    for {set i [expr {int($value - 10)}]} {$i <= [expr {int($value + 10)}]} {incr i} {
        set num $i
        foreach factor $factors {
            while {($num % $factor) == 0} {
                set num [expr {$num / $factor}]
            }
        }
        if {$num == 1} {
            set diff [expr {abs($i - $value)}]
            if {$diff < $min_diff} {
                set min_diff $diff
                set rounded_value $i
            }
        }
    }
    return $rounded_value
}

# PME Grid Size calculation (approximately 1 grid point per Ångström)
set PMEGridSizeX [roundTo235 [expr {$x_basis / 1.0}]]
set PMEGridSizeY [roundTo235 [expr {$y_basis / 1.0}]]
set PMEGridSizeZ [roundTo235 [expr {$z_basis / 1.0}]]

# Round cell basis vectors and PME grid sizes to two decimal places
set x_basis [format "%.2f" $x_basis]
set y_basis [format "%.2f" $y_basis]
set z_basis [format "%.2f" $z_basis]
set PMEGridSizeX [format "%.2f" $PMEGridSizeX]
set PMEGridSizeY [format "%.2f" $PMEGridSizeY]
set PMEGridSizeZ [format "%.2f" $PMEGridSizeZ]

# Open a file to write the output
set filename "PBC-PMEGridSize.txt"
set fileId [open $filename "w"]

# Write PME Grid Sizes (rounded to 2 decimal places)
puts $fileId "PMEGridSizeX  $PMEGridSizeX"
puts $fileId "PMEGridSizeY  $PMEGridSizeY"
puts $fileId "PMEGridSizeZ  $PMEGridSizeZ"

# Write Cell Basis Vectors (rounded to 2 decimal places)
puts $fileId "cellBasisVector1  $x_basis 0.00 0.00"
puts $fileId "cellBasisVector2  0.00 $y_basis 0.00"
puts $fileId "cellBasisVector3  0.00 0.00 $z_basis"

# Write Cell Origin (center of the box)
set centerX [format "%.2f" [lindex $center 0]]
set centerY [format "%.2f" [lindex $center 1]]
set centerZ [format "%.2f" [lindex $center 2]]
puts $fileId "cellOrigin  $centerX $centerY $centerZ"

# Close the file
close $fileId

# Print confirmation to the console
puts "Output written to $filename"
